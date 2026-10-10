import pytest
from src.evaluate import three_state_metrics
from src.feedback import RETAKE, UNCERTAIN, SUITABLE


def test_uncertainty_remains_in_denominators():
    result=three_state_metrics([0,0,0,1,1,1],[RETAKE,UNCERTAIN,SUITABLE,RETAKE,UNCERTAIN,SUITABLE])
    assert result['false_acceptance_rate_all_ungradable']==pytest.approx(1/3)
    assert result['false_rejection_rate_all_gradable']==pytest.approx(1/3)
    assert result['ungradable_retake_recall']==pytest.approx(1/3)
    assert result['decision_coverage']==pytest.approx(2/3)
    assert result['accepted_ungradable_fraction']==.5
    assert result['matrix_rows_actual_0_1_cols_retake_uncertain_suitable']==[[1,1,1],[1,1,1]]


def test_all_uncertain_and_missing_class():
    result=three_state_metrics([1,1],[UNCERTAIN,UNCERTAIN])
    assert result['decision_coverage']==0
    assert result['false_acceptance_rate_all_ungradable'] is None
    assert result['accepted_ungradable_fraction'] is None
    assert result['false_rejection_rate_all_gradable']==0


def test_invalid_states_rejected():
    with pytest.raises(ValueError):three_state_metrics([0],['invented'])
