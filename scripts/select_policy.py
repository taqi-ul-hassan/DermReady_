"""Validation-only policy selection, including a fixed single-image weak-label proxy."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pandas as pd
import torch
from src.model import CaseGradabilityModel
from src.preprocessing import load_image,preprocess_for_inference
from src.quality_features import extract_quality_features,aggregate_quality_features
from src.evaluate import binary_metrics, wilson_interval
from src.feedback import decide_state, SUITABLE, RETAKE, UNCERTAIN


def select_thresholds(labels,scores):
    labels=np.asarray(labels,dtype=int);scores=np.asarray(scores,dtype=float)
    if len(labels)!=len(scores) or set(labels)!={0,1} or not np.isfinite(scores).all():
        raise ValueError('Finite scores and both binary classes are required')
    candidates=np.unique(np.r_[0,scores,1])
    n0=int((labels==0).sum());n1=int((labels==1).sum())
    # Empirical false acceptance <=10% with at least ten accepted cases; no clinical claim.
    acceptable=[]
    for high in candidates:
        accepted=scores>=high
        fa=int(((labels==0)&accepted).sum())/n0
        if fa<=.10 and accepted.sum()>=10:acceptable.append((int(((labels==1)&accepted).sum()),-float(high),float(high)))
    high=max(acceptable)[2] if acceptable else 1.01
    rejection=[]
    for low in candidates:
        if low>=high:continue
        retake=scores<=low
        fr=int(((labels==1)&retake).sum())/n1
        if fr<=.35:rejection.append((int(((labels==0)&retake).sum()),-int(retake.sum()),float(low)))
    low=max(rejection)[2] if rejection else -.01
    states=np.where(scores>=high,2,np.where(scores<=low,0,1))
    return {'retake_below':low,'suitable_above':high,'suitable_enabled':high<=1,
            'selection':'validation scores only; empirical false acceptance <=0.10; retake false rejection <=0.35',
            'validation_cases':len(labels),'validation_ungradable_cases':n0,'validation_gradable_cases':n1,
            'validation_score_band_counts':{'suitable':int((states==2).sum()),'retake':int((states==0).sum()),'uncertain':int((states==1).sum())},
            'false_acceptance_rate_all_ungradable':float(((labels==0)&(states==2)).sum()/n0),
            'false_rejection_rate_all_gradable':float(((labels==1)&(states==0)).sum()/n1),
            'uncertainty_fraction':float((states==1).mean()),
            'rate_denominators':'False acceptance: all ungradable validation cases; false rejection: all gradable validation cases. Uncertain outputs are neither accepted nor rejected.',
            'limits':'Same validation set used for selection; only 23 ungradable cases. These are not held-out test rates or clinically validated safety targets.'}


def run(processed_dir,raw_dir,checkpoint_dir,report_dir):
    processed_dir,raw_dir,checkpoint_dir,report_dir=map(Path,(processed_dir,raw_dir,checkpoint_dir,report_dir))
    torch.set_num_threads(2);torch.backends.nnpack.set_flags(False)
    records=[json.loads(line) for line in (processed_dir/'cases.jsonl').read_text().splitlines()]
    val=[r for r in records if r['split']=='validation']
    checkpoint=torch.load(checkpoint_dir/'best.pt',map_location='cpu',weights_only=True)
    model=CaseGradabilityModel(pretrained=False).eval();model.load_state_dict(checkpoint['state_dict'])
    artifact=joblib.load(checkpoint_dir/'quality_baseline.joblib')
    pipeline=artifact['pipeline'];columns=artifact['columns'];scaler=pipeline.named_steps['standardscaler'];lr=pipeline.named_steps['logisticregression']
    # JSON parameters support safe baseline loading without unpickling at app startup.
    baseline={'columns':columns,'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),
              'coefficient':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0])}
    (checkpoint_dir/'quality_baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    labels=[];cnn_scores=[];feature_scores=[];ids=[];validation_inputs=[]
    for row in val:
        image,metadata=load_image(raw_dir/'images'/Path(row['image_paths'][0]).name)
        with torch.inference_mode():score=float(model(preprocess_for_inference(image).unsqueeze(0)).softmax(1)[0,1])
        image_features=extract_quality_features(image)
        validation_inputs.append((image_features,metadata))
        features=aggregate_quality_features([image_features])
        feature_score=float(pipeline.predict_proba(pd.DataFrame([features])[columns])[0,1])
        labels.append(row['label']);cnn_scores.append(score);feature_scores.append(feature_score);ids.append(row['case_id'])
    policies={};metrics={}
    for name,scores in [('cnn',cnn_scores),('quality_baseline',feature_scores)]:
        policies[name]=select_thresholds(labels,scores);metrics[name]=binary_metrics(labels,scores)
    preferred=max(metrics,key=lambda name:metrics[name]['roc_auc_gradable'])
    quality_thresholds=json.loads((report_dir/'quality_thresholds.json').read_text())
    policy={'preferred_model':preferred,'models':policies,'quality_thresholds':quality_thresholds,
            'input_unit':'one fixed first-listed image per validation case',
            'supervision':'weak proxy: image inherits case label for validation ONLY; not definitive image suitability truth',
            'quality_guard':'Any flagged quality proxy blocks a suitable state; unsupported modes/extremes are uncertain',
            'score_semantics':'uncalibrated research gradability score, not probability of clinical adequacy',
            'test_evaluated':False,'research_only':True}
    pipeline_results={}
    y=np.array(labels)
    for name,scores in [('cnn',cnn_scores),('quality_baseline',feature_scores)]:
        states=np.array([decide_state(score,policies[name],features,metadata,quality_thresholds)[0] for score,(features,metadata) in zip(scores,validation_inputs)])
        n0=int((y==0).sum());n1=int((y==1).sum())
        fa=int(((y==0)&(states==SUITABLE)).sum());fr=int(((y==1)&(states==RETAKE)).sum())
        pipeline_results[name]={'state_counts':{state:int((states==state).sum()) for state in [SUITABLE,RETAKE,UNCERTAIN]},
            'false_acceptance_count':fa,'false_acceptance_rate_all_ungradable':fa/n0,
            'false_acceptance_wilson95':wilson_interval(fa,n0),
            'false_rejection_count':fr,'false_rejection_rate_all_gradable':fr/n1,
            'false_rejection_wilson95':wilson_interval(fr,n1),
            'validation_selection_only':True}
    policy['validation_pipeline_results']=pipeline_results
    policy['preferred_model']=min(pipeline_results,key=lambda name:(pipeline_results[name]['false_acceptance_count'],-(pipeline_results[name]['state_counts'][SUITABLE]-pipeline_results[name]['false_acceptance_count']),-metrics[name]['roc_auc_gradable']))
    policy['model_selection']='Among validation pipelines: fewer false acceptances, then more correctly accepted gradable cases, then ROC-AUC. Selection is preliminary and uses the same validation cohort.'
    (checkpoint_dir/'decision_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    (report_dir/'decision_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    (report_dir/'single_image_validation.json').write_text(json.dumps({'split':'validation','unit':policy['input_unit'],'weak_supervision':True,'test_evaluated':False,'model_metrics_at_0_5':metrics},indent=2)+'\n')
    (processed_dir/'single_image_validation_predictions.json').write_text(json.dumps({'case_ids':ids,'labels':labels,'cnn':cnn_scores,'quality_baseline':feature_scores},indent=2)+'\n')
    print(json.dumps({'preferred_model':policy['preferred_model'],'policies':policies},indent=2))
    return policy

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name,default in [('processed-dir','data/processed'),('raw-dir','data/raw'),('checkpoint-dir','checkpoints'),('report-dir','reports')]:p.add_argument('--'+name,default=default)
    a=p.parse_args();run(a.processed_dir,a.raw_dir,a.checkpoint_dir,a.report_dir)
