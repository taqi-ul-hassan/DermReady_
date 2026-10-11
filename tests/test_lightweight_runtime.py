import subprocess
import sys


def test_indicator_runtime_does_not_import_optional_cnn_dependencies():
    code = '''
import sys, tempfile
from PIL import Image
from src.inference import Predictor
with tempfile.TemporaryDirectory() as d:
    result = Predictor(d, d).predict(Image.new('RGB', (300, 300), 'gray'))
assert result['model'] == 'features_only' and result['score'] is None
assert not any(name in sys.modules for name in ('torch', 'torchvision', 'timm'))
'''
    subprocess.run([sys.executable, '-c', code], check=True)


def test_json_baseline_runtime_preserves_score_without_torch():
    code = '''
import json, math, sys, tempfile
from pathlib import Path
from PIL import Image
from src.inference import Predictor
from src.quality_features import extract_quality_features, aggregate_quality_features
image = Image.new('RGB', (300, 300), 'gray')
columns = list(aggregate_quality_features([extract_quality_features(image)]))
with tempfile.TemporaryDirectory() as d:
    directory = Path(d)
    (directory/'decision_policy.json').write_text(Path('reports/decision_policy.json').read_text())
    baseline = {'columns': columns, 'mean': [0.]*len(columns), 'scale': [1.]*len(columns),
                'coefficient': [0.]*len(columns), 'intercept': .15}
    (directory/'quality_baseline.json').write_text(json.dumps(baseline))
    result = Predictor(d).predict(image)
assert result['model'] == 'quality_baseline'
assert abs(result['score'] - 1/(1+math.exp(-.15))) < 1e-12
assert not any(name in sys.modules for name in ('torch', 'torchvision', 'timm'))
'''
    subprocess.run([sys.executable, '-c', code], check=True)
