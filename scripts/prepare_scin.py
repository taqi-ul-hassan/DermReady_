"""Prepare private case/image manifests and verified grouped train/val/test splits."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import yaml
from src.data_loader import GRADE_COLUMNS, IMAGE_COLUMNS, load_metadata, summarize_votes
from src.splits import SPLIT_NAMES, assign_splits, connected_case_groups, verify_splits


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(raw_dir, processed_dir, split_dir, report_dir, seed=42, fractions=(.70, .15, .15), overwrite=False):
    raw_dir, processed_dir, split_dir, report_dir = map(Path, (raw_dir, processed_dir, split_dir, report_dir))
    inventory_path = raw_dir / 'image_inventory.json'
    if not inventory_path.exists():
        raise ValueError('Run scripts/audit_scin.py first to obtain the object inventory')
    inventory = {r['name']: r for r in json.loads(inventory_path.read_text())}
    _, _, frame = load_metadata(raw_dir)
    records, images = [], []
    for row in frame.to_dict('records'):
        votes = [None if pd.isna(row[c]) else row[c] for c in GRADE_COLUMNS]
        consensus = summarize_votes(votes)
        paths = [row[c] for c in IMAGE_COLUMNS if row[c]]
        missing = [p for p in paths if p not in inventory]
        reasons = []
        if consensus['status'] != 'eligible':
            reasons.append(consensus['status'])
        if not paths:
            reasons.append('no_images')
        if missing:
            reasons.append('incomplete_image_set')
        record = {'case_id': row['case_id'], 'release': row['release'],
                  'raw_votes': votes, **consensus, 'image_paths': paths,
                  'image_count': len(paths), 'missing_image_count': len(missing),
                  'eligible': not reasons, 'exclusion_reasons': reasons}
        records.append(record)
        for i, col in enumerate(IMAGE_COLUMNS, 1):
            if row[col]:
                images.append({'case_id': row['case_id'], 'image_index': i, 'image_path': row[col],
                               'shot_type': row.get(f'image_{i}_shot_type', ''),
                               'object_available': row[col] in inventory,
                               'content_md5': inventory.get(row[col], {}).get('md5Hash', '')})
    groups = connected_case_groups(records, inventory)
    for r in records:
        r['group_id'] = groups[r['case_id']]
    eligible = [r for r in records if r['eligible']]
    assignments = assign_splits(eligible, fractions=fractions, seed=seed)
    leakage = verify_splits(eligible, assignments, inventory)
    for r in records:
        r['split'] = assignments.get(r['case_id'], 'excluded')
    for r in images:
        r['split'] = assignments.get(r['case_id'], 'excluded')
    source_hashes = {p.name:sha256(p) for p in [raw_dir/'scin_cases.csv',raw_dir/'scin_labels.csv',inventory_path]}
    old_provenance = split_dir/'provenance.json'
    if old_provenance.exists() and not overwrite:
        old = json.loads(old_provenance.read_text())
        if old['seed'] != seed or old['requested_fractions'] != dict(zip(SPLIT_NAMES,fractions)) or old['source_sha256'] != source_hashes:
            raise ValueError('Saved split provenance changed; use --overwrite only for an intentional new experiment')
    for directory in (processed_dir, split_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)
    artifacts = []
    cases_path = processed_dir / 'cases.jsonl'
    cases_path.write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in sorted(records, key=lambda r:r['case_id'])))
    artifacts.append(cases_path)
    images_path = processed_dir / 'images.csv'
    pd.DataFrame(images).sort_values(['case_id','image_index']).to_csv(images_path,index=False)
    artifacts.append(images_path)
    split_rows = [{'case_id':r['case_id'],'group_id':r['group_id'],'label':r['label'],
                   'image_count':r['image_count'],'split':assignments[r['case_id']]} for r in eligible]
    split_frame = pd.DataFrame(split_rows).sort_values('case_id')
    full_path = split_dir / 'assignments.csv'
    split_frame.to_csv(full_path,index=False); artifacts.append(full_path)
    split_counts = {}
    for name in SPLIT_NAMES:
        subset = split_frame[split_frame.split == name]
        path = split_dir / f'{name}.csv'
        subset.to_csv(path,index=False);artifacts.append(path)
        split_counts[name] = {'cases':len(subset),'gradable':int((subset.label==1).sum()),
                             'ungradable':int((subset.label==0).sum()),
                             'image_references':int(subset.image_count.sum()),'groups':int(subset.group_id.nunique())}
    report = {'seed':seed,'requested_fractions':dict(zip(SPLIT_NAMES,fractions)),
              'algorithm':'512 seeded group permutations; select by class-count deviation only',
              'label_policy':'At least two unambiguous votes, majority; exclude ties and ambiguous votes',
              'missing_image_policy':'Exclude entire case when any listed image is unavailable; do not transfer set labels to partial sets',
              'group_policy':'Connected components across ALL cases by shared image path or available object MD5',
              'case_count':len(records),'eligible_cases':len(eligible),'excluded_cases':len(records)-len(eligible),
              'exclusion_reason_counts':dict(Counter(reason for r in records for reason in r['exclusion_reasons'])),
              'eligible_class_counts':{'gradable':sum(r['label']==1 for r in eligible),'ungradable':sum(r['label']==0 for r in eligible)},
              'split_counts':split_counts,'leakage_checks':leakage,
              'source_sha256':source_hashes,
              'artifact_sha256':{p.name:sha256(p) for p in artifacts},
              'limitations':['Selected multi-reviewer cohort, not all SCIN cases','Inventory existence is not full image decoding',
                             'No perceptual duplicate detection','Single-image UI differs from case-level supervision'],
              'case_manifest_fields':list(records[0]), 'image_manifest_has_definitive_image_label':False}
    (report_dir/'split_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    # Private provenance sits beside assignments; no row-level records enter reports.
    (split_dir/'provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',default='configs/experiment.yaml')
    p.add_argument('--overwrite',action='store_true',help='Allow intentional replacement with new provenance')
    p.add_argument('--raw-dir');p.add_argument('--processed-dir');p.add_argument('--split-dir');p.add_argument('--report-dir')
    args=p.parse_args();config=yaml.safe_load(Path(args.config).read_text())
    data=config['data']; f=data['split_fractions']
    report=prepare(args.raw_dir or data['raw_dir'],args.processed_dir or data['processed_dir'],
                   args.split_dir or data['split_dir'],args.report_dir or config.get('reports_dir','reports'),
                   seed=config['seed'],fractions=tuple(f[n] for n in SPLIT_NAMES),overwrite=args.overwrite)
    print(json.dumps({k:report[k] for k in ['eligible_cases','excluded_cases','split_counts','leakage_checks']},indent=2))

if __name__=='__main__': main()
