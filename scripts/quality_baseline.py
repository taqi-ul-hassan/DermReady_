"""Fit interpretable feature baseline on train cases; report validation only."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from src.preprocessing import load_image
from src.quality_features import extract_quality_features, aggregate_quality_features
from src.evaluate import binary_metrics


def run(processed_dir,raw_dir,checkpoint_dir,report_dir):
    processed_dir,raw_dir,checkpoint_dir,report_dir=map(Path,(processed_dir,raw_dir,checkpoint_dir,report_dir))
    cases=[json.loads(line) for line in (processed_dir/'cases.jsonl').read_text().splitlines()]
    cases=[r for r in cases if r['split'] in ('train','validation')]
    feature_rows=[];image_rows=[]
    for r in cases:
        features=[]
        for path in r['image_paths']:
            image,_=load_image(raw_dir/'images'/Path(path).name)
            f=extract_quality_features(image);features.append(f)
            image_rows.append({'case_id':r['case_id'],'split':r['split'],'image_path':path,**f})
        feature_rows.append({'case_id':r['case_id'],'split':r['split'],'label':r['label'],**aggregate_quality_features(features)})
    frame=pd.DataFrame(feature_rows);images=pd.DataFrame(image_rows)
    columns=[c for c in frame.columns if c not in ('case_id','split','label')]
    train=frame[frame.split=='train'];val=frame[frame.split=='validation']
    baseline=make_pipeline(StandardScaler(),LogisticRegression(class_weight='balanced',max_iter=2000,random_state=42))
    baseline.fit(train[columns],train.label)
    score=baseline.predict_proba(val[columns])[:,1]
    metrics=binary_metrics(val.label,score);metrics['split']='validation';metrics['model']='quality_features_logistic_regression'
    # Distribution-based flags are proxies, not clinically or technically validated labels.
    v=images[images.split=='validation']
    thresholds={'blur_low':float(v.blur_log_laplacian.quantile(.05)),
                'blur_high':float(v.blur_log_laplacian.quantile(.99)),
                'brightness_low':float(v.brightness_mean.quantile(.05)),
                'brightness_high':float(v.brightness_mean.quantile(.95)),
                'dark_fraction_high':float(v.dark_fraction.quantile(.95)),
                'bright_fraction_high':float(v.bright_fraction.quantile(.95)),
                'minimum_short_side':256,'source':'validation-image distribution: fixed 5th/95th percentiles and 99th-percentile high-frequency guard; not defect ground truth'}
    for directory in (checkpoint_dir,report_dir,processed_dir):directory.mkdir(parents=True,exist_ok=True)
    joblib.dump({'pipeline':baseline,'columns':columns},checkpoint_dir/'quality_baseline.joblib')
    frame.to_csv(processed_dir/'quality_case_features.csv',index=False)
    images.to_csv(processed_dir/'quality_image_features.csv',index=False)
    pd.DataFrame({'case_id':val.case_id,'label':val.label,'score':score}).to_csv(processed_dir/'baseline_validation_predictions.csv',index=False)
    (report_dir/'baseline_validation.json').write_text(json.dumps(metrics,indent=2)+'\n')
    (report_dir/'quality_thresholds.json').write_text(json.dumps(thresholds,indent=2)+'\n')
    print(json.dumps(metrics,indent=2));return metrics

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name,default in [('processed-dir','data/processed'),('raw-dir','data/raw'),('checkpoint-dir','checkpoints'),('report-dir','reports')]:p.add_argument('--'+name,default=default)
    a=p.parse_args();run(a.processed_dir,a.raw_dir,a.checkpoint_dir,a.report_dir)
