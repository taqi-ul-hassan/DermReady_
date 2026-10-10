"""Reproducible SCIN audit; publish aggregates only, keep raw/sample data local."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
import pandas as pd
from PIL import Image
from src.data_loader import GRADE_COLUMNS, IMAGE_COLUMNS, load_metadata, summarize_votes

BASE = 'https://storage.googleapis.com/dx-scin-public-data/'
LIST_URL = 'https://storage.googleapis.com/storage/v1/b/dx-scin-public-data/o'


def fetch(client, url, **kwargs):
    last = None
    for _ in range(3):
        try:
            response = client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, OSError) as exc:
            last = exc
    raise RuntimeError(f'Download failed: {url}') from last


def policy_counts(merged, minimum):
    stats = [summarize_votes(row, minimum) for row in merged[GRADE_COLUMNS].itertuples(index=False, name=None)]
    return {
        'min_valid_votes': minimum,
        'status_counts': dict(Counter(s['status'] for s in stats)),
        'eligible_class_counts': dict(Counter('gradable' if s['label'] == 1 else 'ungradable' for s in stats if s['label'] is not None)),
        'valid_vote_count_distribution': dict(Counter(s['valid_vote_count'] for s in stats)),
        'disagreement_cases': sum(s['disagreement'] for s in stats),
        'multi_valid_vote_cases': sum(s['valid_vote_count'] >= 2 for s in stats),
    }


def audit(raw_dir, output_dir, sample_cases=12, seed=42):
    raw_dir, output_dir = Path(raw_dir), Path(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        provenance = {}
        for filename in ('scin_cases.csv', 'scin_labels.csv'):
            url = BASE + 'dataset/' + filename
            response = fetch(client, url)
            (raw_dir / filename).write_bytes(response.content)
            provenance[filename] = {'url': url, 'sha256': hashlib.sha256(response.content).hexdigest(),
                                    'bytes': len(response.content), 'etag': response.headers.get('etag')}
        cases, labels, merged = load_metadata(raw_dir)
        # Full public object inventory checks existence and exact byte duplicates without downloading all images.
        objects, token = [], None
        while True:
            params = {'prefix': 'dataset/images/', 'maxResults': 1000,
                      'fields': 'items(name,size,contentType,md5Hash),nextPageToken'}
            if token:
                params['pageToken'] = token
            page = fetch(client, LIST_URL, params=params).json()
            objects.extend(page.get('items', []))
            token = page.get('nextPageToken')
            if not token:
                break
        (raw_dir / 'image_inventory.json').write_text(json.dumps(objects))
        inventory = {obj['name']: obj for obj in objects}
        refs = []
        for row in merged.to_dict('records'):
            for index, column in enumerate(IMAGE_COLUMNS, 1):
                if row[column]:
                    refs.append({'case_id': row['case_id'], 'image_index': index, 'path': row[column]})
        refs_frame = pd.DataFrame(refs)
        missing = [r for r in refs if r['path'] not in inventory]
        hashes = Counter(inventory[path].get('md5Hash') for path in set(refs_frame.path) if path in inventory and inventory[path].get('md5Hash'))
        # Balanced deterministic sample by the provisional two-vote consensus; no images embedded in report.
        strict = [summarize_votes(row) for row in merged[GRADE_COLUMNS].itertuples(index=False, name=None)]
        sampling = merged.assign(audit_label=[s['label'] for s in strict])
        selected = []
        for target in (0, 1):
            group = sampling[sampling.audit_label == target]
            selected.extend(group.sample(n=min(len(group), sample_cases // 2), random_state=seed).case_id.tolist())
        selected_refs = [r for r in refs if r['case_id'] in selected]
        sample_dir = raw_dir / 'sample_images'
        sample_dir.mkdir(exist_ok=True)
        def check_image(ref):
            record = dict(ref)
            try:
                blob = fetch(client, BASE + quote(ref['path'], safe='/')).content
                path = sample_dir / Path(ref['path']).name
                path.write_bytes(blob)
                with Image.open(io.BytesIO(blob)) as image:
                    image.load()
                    record.update(format=image.format, mode=image.mode, width=image.width, height=image.height,
                                  readable=True)
            except Exception as exc:
                record.update(readable=False, error=type(exc).__name__)
            return record
        with ThreadPoolExecutor(max_workers=4) as pool:
            checked = list(pool.map(check_image, selected_refs))
    local = {'missing_images': missing, 'sample_checks': checked}
    (raw_dir / 'audit_details.json').write_text(json.dumps(local, indent=2))
    readable = [r for r in checked if r['readable']]
    vote_fields = {c: dict(Counter(merged[c].fillna('').replace('', '<missing>'))) for c in GRADE_COLUMNS}
    report = {
        'source': 'Official SCIN GCS CSVs; full metadata and full object inventory, sampled decoding',
        'seed': seed, 'provenance': provenance,
        'schema_review': {'schema_blob_sha': '4e95a6f01bb8d22586a4274cf173530123b464fc',
                          'license_blob_sha': 'b73abe395e1a01467c215f456fe1b95f80a12a49'},
        'case_rows': len(cases), 'label_rows': len(labels), 'unique_case_ids': int(cases.case_id.nunique()),
        'metadata_columns': len(cases.columns), 'label_columns': len(labels.columns),
        'merge_counts': merged['_merge'].value_counts().to_dict(),
        'labels_without_case': len(set(labels.case_id) - set(cases.case_id)),
        'release_counts': cases.release.value_counts().to_dict(),
        'image_reference_count': len(refs), 'unique_image_paths': int(refs_frame.path.nunique()),
        'repeated_path_groups': int((refs_frame.path.value_counts() > 1).sum()),
        'references_in_repeated_path_groups': int(refs_frame.path.value_counts().loc[lambda x: x > 1].sum()),
        'paths_shared_across_cases': int((refs_frame.groupby('path').case_id.nunique() > 1).sum()),
        'images_per_case': dict(Counter(sum(bool(row[c]) for c in IMAGE_COLUMNS) for row in merged.to_dict('records'))),
        'missing_object_reference_count': len(missing),
        'inventory_objects': len(objects), 'duplicate_content_groups': sum(n > 1 for n in hashes.values()),
        'duplicate_content_unique_paths': sum(n for n in hashes.values() if n > 1),
        'duplicate_detection_scope': 'GCS object MD5 equality among unique referenced paths; not perceptual duplicates',
        'raw_gradability_counts': vote_fields,
        'strict_policy': policy_counts(merged, 2), 'single_vote_policy_for_comparison_only': policy_counts(merged, 1),
        'missingness_counts': {c: int(merged[c].isna().sum() + merged[c].eq('').sum()) for c in merged.columns if c != '_merge'},
        'sample_image_checks': {'selected_cases': len(selected), 'attempted_images': len(checked),
            'readable_images': len(readable), 'failed_images': len(checked)-len(readable),
            'format_counts': dict(Counter(r['format'] for r in readable)),
            'mode_counts': dict(Counter(r['mode'] for r in readable)),
            'width_range': [min(r['width'] for r in readable), max(r['width'] for r in readable)] if readable else [],
            'height_range': [min(r['height'] for r in readable), max(r['height'] for r in readable)] if readable else []},
        'decision': 'GO for research baseline with strict consensus; address missing objects and shared-image/case grouping in step 5',
        'limitations': ['No full-dataset image decoding', 'No perceptual duplicate search',
                        'Gradability is case-level and not a pure blur/exposure label',
                        'No-discernible-pathology votes excluded as semantically ambiguous',
                        'Two-vote cohort is a selected subset; do not generalize its metrics to all SCIN cases'],
    }
    (output_dir / 'data_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dir', default='data/raw')
    parser.add_argument('--output-dir', default='reports')
    parser.add_argument('--sample-cases', type=int, default=12)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.sample_cases < 2:
        parser.error('--sample-cases must be at least 2')
    report = audit(args.raw_dir, args.output_dir, args.sample_cases, args.seed)
    print(json.dumps({k: report[k] for k in ['case_rows','image_reference_count','missing_object_reference_count','strict_policy','sample_image_checks','decision']}, indent=2))
    if not report['sample_image_checks']['readable_images'] or not report['strict_policy']['eligible_class_counts']:
        raise SystemExit('NO-GO: no usable sample or eligible labels')

if __name__ == '__main__':
    main()
