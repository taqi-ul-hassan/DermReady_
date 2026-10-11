import json
import numpy as np
from PIL import Image
from src.artifact_validation import validate_baseline
from src.inference import Predictor
from src.quality_features import aggregate_quality_features,extract_quality_features
from src.feedback import UNCERTAIN
import pytest


def test_baseline_arrays_reject_nonfinite_and_zero_scale():
    columns=list(aggregate_quality_features([extract_quality_features(Image.new('RGB',(300,300),'gray'))]))
    b={'columns':columns,'mean':[0.]*len(columns),'scale':[1.]*len(columns),'coefficient':[0.]*len(columns),'intercept':0.}
    assert validate_baseline(b)==b
    with pytest.raises(ValueError):validate_baseline({**b,'scale':[0.]*len(columns)})
    with pytest.raises(ValueError):validate_baseline({**b,'coefficient':[float('nan')]*len(columns)})


def test_invalid_policy_fails_to_indicators_instead_of_crashing(tmp_path):
    (tmp_path/'decision_policy.json').write_text('{broken')
    predictor=Predictor(tmp_path,report_dir=tmp_path)
    result=predictor.predict(Image.new('RGB',(300,300),'gray'))
    assert result['state']==UNCERTAIN and result['score'] is None
    assert 'invalid' in result['feedback'] and 'unavailable' in result['decision_reason']


def test_saved_frozen_policy_validates_without_changing_bands():
    from pathlib import Path
    from src.artifact_validation import validate_policy
    policy=json.loads(Path('reports/decision_policy.json').read_text())
    before=json.dumps(policy,sort_keys=True)
    validate_policy(policy)
    assert json.dumps(policy,sort_keys=True)==before


def test_invalid_baseline_falls_back_with_warning(tmp_path):
    from pathlib import Path
    (tmp_path/'decision_policy.json').write_text(Path('reports/decision_policy.json').read_text())
    (tmp_path/'quality_baseline.json').write_text('{broken')
    result=Predictor(tmp_path,report_dir=tmp_path).predict(Image.new('RGB',(300,300),'gray'))
    assert result['model']=='features_only' and result['score'] is None
    assert 'Feature baseline is invalid' in result['feedback']


@pytest.mark.parametrize('models',[['cnn'], 'cnn', None])
def test_malformed_models_object_falls_back_without_startup_crash(tmp_path,models):
    from pathlib import Path
    policy=json.loads(Path('reports/decision_policy.json').read_text());policy['models']=models
    (tmp_path/'decision_policy.json').write_text(json.dumps(policy))
    assert Predictor(tmp_path,tmp_path).mode=='features_only'


def test_string_band_rejected_before_prediction(tmp_path):
    from pathlib import Path
    policy=json.loads(Path('reports/decision_policy.json').read_text())
    policy['models']['quality_baseline']['retake_below']='0.5'
    (tmp_path/'decision_policy.json').write_text(json.dumps(policy))
    assert Predictor(tmp_path,tmp_path).mode=='features_only'

