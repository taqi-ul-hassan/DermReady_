import csv
import json
import pytest
from src.artifact_identity import sha256
from src.experiment_integrity import verified_cases


def experiment(tmp_path):
    processed, splits, raw = (tmp_path/n for n in ('processed','splits','raw'))
    for p in (processed,splits,raw):p.mkdir()
    rows=[]
    for split in ('train','validation','test'):
        for label in (0,1):
            name=f'{split}{label}'
            rows.append({'case_id':name,'group_id':name,'label':label,'eligible':True,
                         'split':split,'image_paths':[f'dataset/images/{name}.png'],'image_count':1})
    (processed/'cases.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (processed/'images.csv').write_text('case_id,image_path\n')
    columns=['case_id','group_id','label','image_count','split']
    for name in ('assignments','train','validation','test'):
        with (splits/(name+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
            writer.writerows({k:r[k] for k in columns} for r in rows if name=='assignments' or r['split']==name)
    (raw/'scin_cases.csv').write_text('case_id\n')
    (raw/'scin_labels.csv').write_text('case_id\n')
    (raw/'image_inventory.json').write_text(json.dumps([{'name':r['image_paths'][0]} for r in rows]))
    refresh(processed,splits,raw)
    return processed,splits,raw


def refresh(processed,splits,raw):
    provenance={'artifact_sha256':{p.name:sha256(p) for d in (processed,splits) for p in d.iterdir() if p.name!='provenance.json'},
                'source_sha256':{p.name:sha256(p) for p in raw.iterdir()}}
    (splits/'provenance.json').write_text(json.dumps(provenance))


def test_verified_manifest_returns_cases_and_new_freeze_hashes(tmp_path):
    dirs=experiment(tmp_path)
    rows, hashes=verified_cases(*dirs)
    assert len(rows)==6 and set(hashes)=={'processed/cases.jsonl','processed/images.csv','splits/provenance.json'}


@pytest.mark.parametrize('where,name',[('processed','cases.jsonl'),('processed','images.csv'),('splits','test.csv'),('raw','image_inventory.json')])
def test_changed_inputs_block_evaluation(tmp_path,where,name):
    dirs=experiment(tmp_path)
    path=tmp_path/where/name
    path.write_text(path.read_text()+'\n')
    with pytest.raises(ValueError,match='provenance'):verified_cases(*dirs)


def test_manifest_and_split_metadata_must_agree_even_with_updated_hashes(tmp_path):
    processed,splits,raw=experiment(tmp_path)
    path=processed/'cases.jsonl';rows=[json.loads(s) for s in path.read_text().splitlines()]
    rows[-1]['label']=0
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    refresh(processed,splits,raw)
    with pytest.raises(ValueError,match='metadata'):verified_cases(processed,splits,raw)


def test_evaluation_fails_before_cache_or_report_freeze(tmp_path,monkeypatch):
    from scripts import evaluate_test
    processed,splits,raw=experiment(tmp_path)
    (processed/'cases.jsonl').write_text('{}\n')
    monkeypatch.setattr(evaluate_test,'cache',lambda *a,**k:pytest.fail('Image access before verification'))
    reports=tmp_path/'reports'
    with pytest.raises(ValueError,match='provenance'):
        evaluate_test.run(processed,raw,tmp_path/'checkpoints',splits,reports)
    assert not (reports/'test_freeze.json').exists()
