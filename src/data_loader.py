"""SCIN metadata loading and explicit gradability parsing; see src.splits for splitting."""
from pathlib import Path
import pandas as pd

GRADE_COLUMNS = [f'dermatologist_gradable_for_skin_condition_{i}' for i in (1, 2, 3)]
IMAGE_COLUMNS = [f'image_{i}_path' for i in (1, 2, 3)]
GRADE_MAP = {
    'DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT': 1,
    'NO_IMAGE_QUALITY_INSUFFICIENT': 0,
    # Keep this semantically ambiguous category outside the binary task.
    'YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY': None,
}


def parse_gradability(value):
    if value is None or pd.isna(value) or str(value).strip() == '':
        return None
    token = str(value).strip()
    if token not in GRADE_MAP:
        raise ValueError(f'Unrecognized SCIN gradability token: {token!r}; review schema before proceeding')
    return GRADE_MAP[token]


def summarize_votes(values, min_votes=2):
    votes = [parse_gradability(v) for v in values]
    valid = [v for v in votes if v is not None]
    result = {'valid_vote_count': len(valid), 'gradable_votes': valid.count(1),
              'ungradable_votes': valid.count(0), 'disagreement': len(set(valid)) > 1,
              'label': None, 'status': 'insufficient_votes'}
    if len(valid) >= min_votes:
        if result['gradable_votes'] == result['ungradable_votes']:
            result['status'] = 'tie'
        else:
            result['label'] = int(result['gradable_votes'] > result['ungradable_votes'])
            result['status'] = 'eligible'
    return result


def load_metadata(raw_dir):
    raw_dir = Path(raw_dir)
    cases = pd.read_csv(raw_dir / 'scin_cases.csv', dtype=str, keep_default_na=False)
    labels = pd.read_csv(raw_dir / 'scin_labels.csv', dtype=str, keep_default_na=False)
    for name, frame, columns in [('cases', cases, ['case_id', *IMAGE_COLUMNS]),
                                 ('labels', labels, ['case_id', *GRADE_COLUMNS])]:
        missing = set(columns) - set(frame.columns)
        if missing:
            raise ValueError(f'{name} missing required columns: {sorted(missing)}')
        if frame.case_id.eq('').any() or frame.case_id.duplicated().any():
            raise ValueError(f'{name} has empty or duplicate case IDs')
    # Preserve unlabeled cases; audit the merge instead of silently inner-joining.
    merged = cases.merge(labels, on='case_id', how='left', validate='one_to_one', indicator=True)
    return cases, labels, merged
