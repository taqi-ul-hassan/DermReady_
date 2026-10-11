"""Identify published artifacts without loading weights or reading user images."""
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_identity(checkpoint_dir, manifest_path, model=None):
    try:
        expected = json.loads(Path(manifest_path).read_text())['artifact_sha256']
        names = ('best.pt', 'quality_baseline.json', 'decision_policy.json')
        if not isinstance(expected, dict) or any(
            not isinstance(expected.get(n), str) or len(expected[n]) != 64 for n in names
        ):
            raise ValueError('Invalid published artifact manifest')
    except (OSError, ValueError, KeyError, TypeError):
        return {'status': 'unavailable', 'files': {}, 'active_model_matches': False}
    files = {}
    for name in names:
        path = Path(checkpoint_dir) / name
        try:
            files[name] = 'matched' if sha256(path) == expected[name] else 'different'
        except FileNotFoundError:
            files[name] = 'missing'
        except OSError:
            files[name] = 'unreadable'
    required = {
        'quality_baseline': ('quality_baseline.json', 'decision_policy.json'),
        'cnn': ('best.pt', 'decision_policy.json'),
    }.get(model, ())
    matched = bool(required) and all(files[n] == 'matched' for n in required)
    return {'status': 'checked', 'files': files, 'active_model_matches': matched}


def evidence_identity_message(identity, mode):
    if mode == 'features_only':
        return 'Historical results below describe the published fitted systems. This session uses capture indicators only.'
    if identity['active_model_matches']:
        return 'The active model and decision policy match the published artifact hashes. These are historical evaluation results, not an assessment of your upload.'
    return 'The active artifacts could not be matched to the published evaluation. Historical results below must not be attributed to this installation.'
