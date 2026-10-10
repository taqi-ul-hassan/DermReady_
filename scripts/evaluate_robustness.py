"""Paired stress tests of frozen app policies; no tuning or clinical labels for edits."""
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
from src.inference import Predictor
from src.preprocessing import load_image
from src.perturbations import CONDITIONS, degrade
from src.feedback import RETAKE, UNCERTAIN, SUITABLE


def run(processed_dir='data/processed',raw_dir='data/raw',checkpoint_dir='checkpoints',report_dir='reports'):
    processed_dir,raw_dir,checkpoint_dir,report_dir=map(Path,(processed_dir,raw_dir,checkpoint_dir,report_dir))
    report_dir.mkdir(parents=True,exist_ok=True)
    output=report_dir/'robustness.json'
    if output.exists():raise FileExistsError('Stress-test report already exists; do not tune on these results.')
    frozen=json.loads((report_dir/'test_freeze.json').read_text())['sha256']
    artifact_names=['best.pt','quality_baseline.json','decision_policy.json']
    def hashes():return {n:hashlib.sha256((checkpoint_dir/n).read_bytes()).hexdigest() for n in artifact_names}
    before=hashes()
    if before!={n:frozen[n] for n in artifact_names}:raise ValueError('Artifacts differ from final held-out evaluation')
    protocol={'cases':'all held-out cases, first-listed image; paired within case',
              'conditions':CONDITIONS,'frozen_sha256':before,
              'interpretation':'Controlled edits have no new clinical suitability labels. Report state transitions, capture proxies and score sensitivity, not corruption accuracy. No model, policy or default changes.'}
    (report_dir/'robustness_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    rows=sorted([json.loads(s) for s in (processed_dir/'cases.jsonl').read_text().splitlines() if json.loads(s)['split']=='test'],key=lambda r:r['case_id'])
    predictors={name:Predictor(checkpoint_dir,model_name=name) for name in ['quality_baseline','cnn']}
    private=[]
    for row in rows:
        image,_=load_image(raw_dir/'images'/Path(row['image_paths'][0]).name)
        record={'case_id':row['case_id'],'conditions':{}}
        for condition in CONDITIONS:
            edited=degrade(image,condition)
            record['conditions'][condition]={}
            for name,predictor in predictors.items():
                result=predictor.predict(edited)
                record['conditions'][condition][name]={k:result[k] for k in ['state','score','features','flags']}
        private.append(record)
    summary={'cases':len(rows),'protocol':protocol,'models':{},'limits':[
        'Original case gradability labels are not ground truth for edited images.',
        'Blur radius is in source-image pixels; response depends on original resolution.',
        'No tuning or safety guarantee. Synthetic edits do not cover real camera or patient variation.']}
    states=[RETAKE,UNCERTAIN,SUITABLE]
    for name in predictors:
        baseline=[r['conditions']['original'][name] for r in private]
        accepted=[i for i,r in enumerate(baseline) if r['state']==SUITABLE]
        model={}
        for condition in CONDITIONS:
            results=[r['conditions'][condition][name] for r in private]
            transition=[[sum(a['state']==s and b['state']==t for a,b in zip(baseline,results)) for t in states] for s in states]
            model[condition]={'state_counts':{s:sum(r['state']==s for r in results) for s in states},
                'transition_rows_original_cols_edited_retake_uncertain_suitable':transition,
                'original_suitable_count':len(accepted),
                'original_suitable_still_suitable':sum(results[i]['state']==SUITABLE for i in accepted),
                'median_score':float(np.median([r['score'] for r in results])),
                'median_paired_score_change':float(np.median([b['score']-a['score'] for a,b in zip(baseline,results)])),
                'feature_medians':{f:float(np.median([r['features'][f] for r in results])) for f in baseline[0]['features']},
                'flag_counts':{f:sum(f in r['flags'] for r in results) for f in ['focus','dark','bright','resolution','unusual_texture']}}
        summary['models'][name]=model
    if hashes()!=before:raise RuntimeError('Artifacts changed during stress tests')
    (processed_dir/'robustness_predictions.json').write_text(json.dumps(private,indent=2)+'\n')
    output.write_text(json.dumps(summary,indent=2)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    x=np.arange(len(CONDITIONS))
    for ax,(name,model) in zip(axes,summary['models'].items()):
        bottom=np.zeros(len(x))
        for state,color in zip(states,['#ed9958','#aab4be','#51a994']):
            values=np.array([model[c]['state_counts'][state] for c in CONDITIONS])
            ax.bar(x,values,bottom=bottom,label=state,color=color);bottom+=values
        ax.set_xticks(x,['Original','Blur 2px','Blur 5px','Dark ×0.35','Bright ×1.8'],rotation=25,ha='right')
        ax.set_ylabel('Cases (one image each)');ax.set_ylim(0,len(rows));ax.set_title(name.replace('_',' ').title())
    axes[1].legend(fontsize=8,loc='upper left');fig.suptitle('Frozen policies under controlled capture degradations')
    fig.savefig(report_dir/'robustness_states.png',dpi=160);plt.close(fig)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name,default in [('processed-dir','data/processed'),('raw-dir','data/raw'),('checkpoint-dir','checkpoints'),('report-dir','reports')]:p.add_argument('--'+name,default=default)
    a=p.parse_args();print(json.dumps(run(**vars(a)),indent=2))
