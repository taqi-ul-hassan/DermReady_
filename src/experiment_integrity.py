"""Bind evaluation inputs to saved private split provenance before image access."""
import csv
import json
from pathlib import Path
from .artifact_identity import sha256
from .splits import SPLIT_NAMES, verify_splits


def verified_cases(processed_dir, split_dir, raw_dir):
    processed_dir, split_dir, raw_dir = map(Path, (processed_dir, split_dir, raw_dir))
    provenance = json.loads((split_dir / 'provenance.json').read_text())
    paths = {n: processed_dir / n for n in ('cases.jsonl', 'images.csv')}
    paths.update({n: split_dir / n for n in ('assignments.csv', 'train.csv', 'validation.csv', 'test.csv')})
    for name, path in paths.items():
        if sha256(path) != provenance['artifact_sha256'].get(name):
            raise ValueError('Prepared artifacts differ from saved split provenance: ' + name)
    for name in ('scin_cases.csv', 'scin_labels.csv', 'image_inventory.json'):
        if sha256(raw_dir / name) != provenance['source_sha256'].get(name):
            raise ValueError('Source artifacts differ from saved split provenance: ' + name)
    records = [json.loads(line) for line in paths['cases.jsonl'].read_text().splitlines()]
    ids = [r['case_id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate case IDs in prepared manifest')
    eligible = [r for r in records if r['eligible']]
    if any(r['split'] not in SPLIT_NAMES or r['label'] not in (0, 1) or not r['image_paths']
           or r['image_count'] != len(r['image_paths']) for r in eligible):
        raise ValueError('Invalid eligible case in prepared manifest')
    if any(r['split'] != 'excluded' for r in records if not r['eligible']):
        raise ValueError('Excluded cases have an evaluation split')
    for split in SPLIT_NAMES:
        with paths[split + '.csv'].open(newline='') as stream:
            saved = list(csv.DictReader(stream))
        actual = {r['case_id']: r for r in eligible if r['split'] == split}
        if len(saved) != len(actual) or {r['case_id'] for r in saved} != set(actual):
            raise ValueError('Case manifest does not match saved split: ' + split)
        for row in saved:
            case = actual[row['case_id']]
            if row['split'] != split or row['group_id'] != case['group_id'] or int(row['label']) != case['label'] or int(row['image_count']) != case['image_count']:
                raise ValueError('Case metadata does not match saved split: ' + split)
    inventory = {r['name']: r for r in json.loads((raw_dir / 'image_inventory.json').read_text())}
    verify_splits(eligible, {r['case_id']: r['split'] for r in eligible}, inventory)
    hashes = {'processed/' + n: sha256(p) for n, p in paths.items() if n in ('cases.jsonl', 'images.csv')}
    hashes['splits/provenance.json'] = sha256(split_dir / 'provenance.json')
    return records, hashes
