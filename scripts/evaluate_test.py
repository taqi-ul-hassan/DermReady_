"""Evaluate frozen artifacts once on held-out cases; never select/tune using test data."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch
from scripts.cache_images import cache
from src.evaluate import binary_metrics, three_state_metrics
from src.feedback import SUITABLE, RETAKE, UNCERTAIN
from src.inference import Predictor
from src.preprocessing import load_image, preprocess_for_inference
from src.quality_features import extract_quality_features, aggregate_quality_features
from src.experiment_integrity import verified_cases


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def baseline_score(features, baseline):
    x=np.array([features[name] for name in baseline['columns']])
    z=((x-np.array(baseline['mean']))/np.array(baseline['scale']))@np.array(baseline['coefficient'])+baseline['intercept']
    return float(1/(1+np.exp(-np.clip(z,-40,40))))


def run(processed_dir='data/processed', raw_dir='data/raw', checkpoint_dir='checkpoints',
        split_dir='data/splits', report_dir='reports'):
    processed_dir,raw_dir,checkpoint_dir,split_dir,report_dir=map(Path,(processed_dir,raw_dir,checkpoint_dir,split_dir,report_dir))
    report_dir.mkdir(parents=True,exist_ok=True)
    output=report_dir/'heldout_test.json'
    if output.exists():
        raise FileExistsError('Test report already exists. Inspect it; do not repeatedly tune against this cohort.')
    records, manifest_hashes = verified_cases(processed_dir, split_dir, raw_dir)
    frozen_paths={name:checkpoint_dir/name for name in ['best.pt','quality_baseline.json','decision_policy.json']}
    frozen_paths.update({f'splits/{name}.csv':split_dir/f'{name}.csv' for name in ['train','validation','test']})
    frozen_paths.update({'processed/cases.jsonl':processed_dir/'cases.jsonl',
                         'processed/images.csv':processed_dir/'images.csv',
                         'splits/provenance.json':split_dir/'provenance.json'})
    hashes={name:digest(path) for name,path in frozen_paths.items()}
    policy=json.loads((checkpoint_dir/'decision_policy.json').read_text())
    freeze={'sha256':hashes,'preferred_model':policy['preferred_model'],
            'protocol':'All artifacts, splits and default model frozen before downloading held-out images. Binary threshold fixed at 0.5. Single-image view fixed to first listed path. No test tuning.'}
    (report_dir/'test_freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    decoded=cache(processed_dir,raw_dir,report_dir/'test_decode',splits=('test',))
    if decoded['failed_images']:raise RuntimeError('Test decoding failed: resolve input access without dropping cases.')
    predictors={name:Predictor(checkpoint_dir,model_name=name) for name in ['cnn','quality_baseline']}
    rows=sorted([r for r in records if r['split']=='test'],key=lambda r:r['case_id'])
    if not rows:raise ValueError('No test cases')
    private=[]
    for row in rows:
        images=[load_image(raw_dir/'images'/Path(path).name)[0] for path in row['image_paths']]
        tensors=torch.stack([preprocess_for_inference(image) for image in images])
        with torch.inference_mode():
            indices=torch.zeros(len(images),dtype=torch.long)
            cnn=float(predictors['cnn'].model(tensors,indices,1).softmax(1)[0,1])
        features=aggregate_quality_features([extract_quality_features(image) for image in images])
        baseline=baseline_score(features,predictors['quality_baseline'].baseline)
        first=raw_dir/'images'/Path(row['image_paths'][0]).name
        single={}
        for name,predictor in predictors.items():
            result=predictor.predict(first)
            single[name]={'score':result['score'],'state':result['state'],'flags':result['flags']}
        private.append({'case_id':row['case_id'],'label':row['label'],'image_count':len(images),
                        'case_scores':{'cnn':cnn,'quality_baseline':baseline},'single_image':single})
    labels=[r['label'] for r in private]
    result={'split':'test','cases':len(rows),'image_references':sum(r['image_count'] for r in private),
            'frozen_artifacts':freeze,'selected_default_model':policy['preferred_model'],
            'class_order':['ungradable','gradable'],'case_binary':{},'single_image_weak_proxy':{},
            'limitations':['Single-image labels inherit case labels; these are not definitive image-level suitability labels.',
                          'Only 23 ungradable held-out cases; intervals are wide. No clinical safety or diagnosis claim.',
                          'The test cohort is now consumed for final reporting. Future changes require new independent evaluation.',
                          'Thresholds and default model remain validation-selected; test outcomes do not change the app.']}
    for name in predictors:
        result['case_binary'][name]=binary_metrics(labels,[r['case_scores'][name] for r in private])
        result['single_image_weak_proxy'][name]={
            'binary_at_0_5':binary_metrics(labels,[r['single_image'][name]['score'] for r in private]),
            'pipeline':three_state_metrics(labels,[r['single_image'][name]['state'] for r in private])}
    _, after_manifests = verified_cases(processed_dir, split_dir, raw_dir)
    if after_manifests != manifest_hashes or hashes!={name:digest(path) for name,path in frozen_paths.items()}:
        raise RuntimeError('Frozen artifacts/splits changed during evaluation; results blocked.')
    (processed_dir/'heldout_test_predictions.json').write_text(json.dumps(private,indent=2)+'\n')
    output.write_text(json.dumps(result,indent=2)+'\n')
    fig,axes=plt.subplots(2,2,figsize=(9,7),layout='constrained')
    for col,name in enumerate(predictors):
        for row,key in enumerate(['case_binary','single_image_weak_proxy']):
            metrics=result[key][name] if row==0 else result[key][name]['pipeline']
            matrix=np.array(metrics['confusion_matrix_rows_actual_0_1_cols_predicted_0_1'] if row==0 else metrics['matrix_rows_actual_0_1_cols_retake_uncertain_suitable'])
            ax=axes[row,col];ax.imshow(matrix,cmap='Blues',vmin=0)
            ax.set_xticks(range(matrix.shape[1]),['Ungradable','Gradable'] if row==0 else ['Retake','Uncertain','Suitable'])
            ax.set_yticks([0,1],['Ungradable','Gradable']);ax.set_ylabel('Actual case label')
            ax.set_title(f'{name}: '+('all-image case' if row==0 else 'first-image weak proxy'))
            for (i,j),value in np.ndenumerate(matrix):ax.text(j,i,str(value),ha='center',va='center')
    fig.suptitle('Frozen held-out evaluation (107 cases)');fig.savefig(report_dir/'heldout_confusion.png',dpi=160);plt.close(fig)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name,default in [('processed-dir','data/processed'),('raw-dir','data/raw'),('checkpoint-dir','checkpoints'),('split-dir','data/splits'),('report-dir','reports')]:
        parser.add_argument('--'+name,default=default)
    args=parser.parse_args();print(json.dumps(run(**{key.replace('-','_'):value for key,value in vars(args).items()}),indent=2))

