from pathlib import Path
import json
import numpy as np
from PIL import Image
import pytest
from src.inference import Predictor
from src.feedback import UNCERTAIN


def test_missing_artifacts_are_explicit_features_only(tmp_path):
    predictor=Predictor(tmp_path,report_dir=tmp_path)
    result=predictor.predict(Image.new('RGB',(300,300),'gray'))
    assert result['state']==UNCERTAIN and result['score'] is None
    assert result['model']=='features_only' and 'unavailable' in result['feedback']
    with pytest.raises(ValueError):predictor.predict(b'corrupt')


def test_real_cpu_checkpoint_and_json_baseline_round_trip():
    if not Path('checkpoints/best.pt').exists() or not Path('checkpoints/decision_policy.json').exists():
        pytest.skip('Private trained artifacts required; generate with documented pipeline')
    image=Image.fromarray(np.random.default_rng(42).integers(20,230,(300,400,3),dtype=np.uint8))
    cnn=Predictor(model_name='cnn');first=cnn.predict(image);second=cnn.predict(image)
    assert first['score']==second['score'] and 0<=first['score']<=1
    assert first['model']=='cnn'
    baseline=Predictor(model_name='quality_baseline').predict(image)
    assert 0<=baseline['score']<=1 and baseline['model']=='quality_baseline'
    assert 'clinical' in first['feedback'] or 'clinician' in first['feedback']


def test_app_constructs_without_model_or_public_server(tmp_path):
    from app import build_app
    app=build_app(Predictor(tmp_path,report_dir=tmp_path))
    assert app.config['analytics_enabled'] is False
    assert app.delete_cache==(30,60)
