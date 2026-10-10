import json
import pytest
from src.splits import assign_splits, connected_case_groups, verify_splits


def test_transitive_groups_include_excluded_cases_and_content_duplicates():
    records = [
        {'case_id':'a','image_paths':['p1']},
        {'case_id':'excluded_bridge','image_paths':['p1','p2']},
        {'case_id':'b','image_paths':['p2']},
        {'case_id':'c','image_paths':['different_name']},
        {'case_id':'d','image_paths':['independent']},
    ]
    inventory = {'p1':{'md5Hash':'x'},'p2':{'md5Hash':'y'},'different_name':{'md5Hash':'y'},'independent':{'md5Hash':'z'}}
    groups=connected_case_groups(records,inventory)
    assert groups['a']==groups['excluded_bridge']==groups['b']==groups['c']
    assert groups['d']!=groups['a']
    assert groups==connected_case_groups(list(reversed(records)),inventory)


def sample_records():
    return [{'case_id':str(i),'group_id':str(i//2),'label':i%2,'image_paths':[f'p{i}']} for i in range(40)]


def test_grouped_assignment_is_reproducible_and_contains_both_classes():
    records=sample_records()
    assignments=assign_splits(records,seed=42)
    assert assignments==assign_splits(list(reversed(records)),seed=42)
    for name in ('train','validation','test'):
        assert {r['label'] for r in records if assignments[r['case_id']]==name}=={0,1}
    inventory={r['image_paths'][0]:{} for r in records}
    assert not any(verify_splits(records,assignments,inventory).values())
    for i in range(0,40,2): assert assignments[str(i)]==assignments[str(i+1)]


@pytest.mark.parametrize('kind',['group','path','md5'])
def test_verifier_rejects_cross_split_leakage(kind):
    records=[{'case_id':'a','group_id':'ga','label':0,'image_paths':['pa']},
             {'case_id':'b','group_id':'gb','label':1,'image_paths':['pb']}]
    inventory={'pa':{},'pb':{}}
    if kind=='group':records[1]['group_id']='ga'
    if kind=='path':records[1]['image_paths']=['pa']
    if kind=='md5':inventory={'pa':{'md5Hash':'same'},'pb':{'md5Hash':'same'}}
    with pytest.raises(ValueError,match='leakage'):
        verify_splits(records,{'a':'train','b':'test'},inventory)


def test_insufficient_groups_and_missing_assignment_fail():
    with pytest.raises(ValueError,match='independent'):
        assign_splits(sample_records()[:2])
    with pytest.raises(ValueError,match='assignments'):
        verify_splits(sample_records(),{}, {})


def test_preparation_excludes_incomplete_sets_and_preserves_provenance(tmp_path):
    import pandas as pd
    from scripts.prepare_scin import prepare
    from src.data_loader import GRADE_COLUMNS, IMAGE_COLUMNS
    raw=tmp_path/'raw';raw.mkdir()
    cases=[]; labels=[];objects=[]
    for i in range(30):
        cid=str(i);paths={c:'' for c in IMAGE_COLUMNS};paths['image_1_path']=f'p{i}'
        cases.append({'case_id':cid,'release':'test',**paths})
        token='DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT' if i%2 else 'NO_IMAGE_QUALITY_INSUFFICIENT'
        labels.append({'case_id':cid,**{c:token for c in GRADE_COLUMNS}})
        if i!=0:objects.append({'name':f'p{i}'})
    pd.DataFrame(cases).to_csv(raw/'scin_cases.csv',index=False)
    pd.DataFrame(labels).to_csv(raw/'scin_labels.csv',index=False)
    (raw/'image_inventory.json').write_text(json.dumps(objects))
    args=(raw,tmp_path/'processed',tmp_path/'splits',tmp_path/'reports')
    first=prepare(*args)
    second=prepare(*args)
    assert first['artifact_sha256']==second['artifact_sha256']
    assert first['eligible_cases']==29
    assert first['exclusion_reason_counts']=={'incomplete_image_set':1}
    records=[json.loads(line) for line in (args[1]/'cases.jsonl').read_text().splitlines()]
    excluded=next(r for r in records if r['case_id']=='0')
    assert excluded['split']=='excluded' and excluded['raw_votes']==[labels[0][c] for c in GRADE_COLUMNS]
    images=pd.read_csv(args[1]/'images.csv')
    assert 'label' not in images.columns
    with pytest.raises(ValueError,match='provenance changed'):
        prepare(*args,seed=99)
