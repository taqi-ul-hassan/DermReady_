from pathlib import Path

import pytest

from src.capture_review import compare_captures, evidence_summary, primary_action

ROOT = Path(__file__).resolve().parents[1]


def test_retake_comparison_measures_blur_without_suitability_claim():
    original = ROOT/'assets/demo/synthetic_original.png'
    blurred = ROOT/'assets/demo/synthetic_blur.png'
    first, second, rows, notes = compare_captures(blurred, original)
    assert first.size == second.size
    focus = next(row for row in rows if row[0] == 'Focus proxy')
    assert focus[2] > focus[1] and focus[3] > 0
    assert 'focus proxy increased' in notes
    assert 'No clinical improvement or suitability is established' in notes
    assert not any('score' in row[0].lower() for row in rows)


def test_comparison_requires_two_valid_images(tmp_path):
    with pytest.raises(ValueError, match='both'):
        compare_captures(None, None)
    invalid = tmp_path/'invalid.png'
    invalid.write_bytes(b'not an image')
    with pytest.raises(ValueError, match='corrupt'):
        compare_captures(invalid, ROOT/'assets/demo/synthetic_original.png')


def test_evidence_includes_abstention_and_correct_error_denominators():
    rows = evidence_summary(ROOT/'reports/heldout_test.json')
    baseline = next(row for row in rows if row[0] == 'quality_baseline')
    assert baseline[1:] == ['4.3%', '29.8%', '43.0%', '57.0%']
    assert evidence_summary(ROOT/'missing.json') == []


def test_primary_action_prioritizes_supported_guidance_and_missing_artifacts():
    result = {'model': 'quality_baseline', 'flags': ['focus', 'dark']}
    assert 'tap to focus' in primary_action(result)
    assert 'no fitted suitability decision' in primary_action({**result, 'model': 'features_only'})
