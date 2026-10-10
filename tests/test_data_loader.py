import pandas as pd
import pytest
from src.data_loader import GRADE_COLUMNS, IMAGE_COLUMNS, load_metadata, parse_gradability, summarize_votes

YES = 'DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT'
NO = 'NO_IMAGE_QUALITY_INSUFFICIENT'
AMBIGUOUS = 'YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY'


def test_categorical_labels_are_not_python_truthiness():
    assert parse_gradability(NO) == 0
    assert parse_gradability(YES) == 1
    assert parse_gradability(AMBIGUOUS) is None
    assert parse_gradability('') is None
    assert parse_gradability(float('nan')) is None
    with pytest.raises(ValueError):
        parse_gradability('NEW_UNDOCUMENTED_VALUE')


def test_consensus_preserves_missing_and_disagreement():
    assert summarize_votes([YES, '', ''])['label'] is None
    assert summarize_votes([YES, NO, ''])['status'] == 'tie'
    result = summarize_votes([YES, YES, NO])
    assert result['label'] == 1 and result['disagreement']
    assert summarize_votes([NO, NO, AMBIGUOUS])['label'] == 0
    assert summarize_votes([AMBIGUOUS, '', ''])['valid_vote_count'] == 0


def write_tables(root, duplicate=False):
    cases = pd.DataFrame([{'case_id': 'a', **{c: '' for c in IMAGE_COLUMNS}},
                          {'case_id': 'a' if duplicate else 'b', **{c: '' for c in IMAGE_COLUMNS}}])
    labels = pd.DataFrame([{'case_id': 'a', **{c: YES for c in GRADE_COLUMNS}}])
    cases.to_csv(root / 'scin_cases.csv', index=False)
    labels.to_csv(root / 'scin_labels.csv', index=False)


def test_loader_preserves_unlabeled_cases(tmp_path):
    write_tables(tmp_path)
    _, _, merged = load_metadata(tmp_path)
    assert len(merged) == 2
    assert merged['_merge'].astype(str).tolist() == ['both', 'left_only']


def test_loader_rejects_duplicate_case_ids(tmp_path):
    write_tables(tmp_path, duplicate=True)
    with pytest.raises(ValueError, match='duplicate case IDs'):
        load_metadata(tmp_path)
