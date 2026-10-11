"""Check fitted-model readiness and published identity; no uploads or downloads."""
import argparse
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.artifact_identity import artifact_identity


def check_installation(checkpoint_dir=None):
    directory = Path(checkpoint_dir) if checkpoint_dir else ROOT / 'checkpoints'
    identity = artifact_identity(directory, ROOT / 'reports/model_artifacts.json')
    report = {'python': platform.python_version(), 'active_model': None,
              'trained_ready': False, 'published_identity': identity, 'messages': []}
    try:
        from src.inference import Predictor
        predictor = Predictor(directory, ROOT / 'reports')
        report['active_model'] = predictor.mode
        report['trained_ready'] = predictor.mode != 'features_only'
        report['published_identity'] = artifact_identity(
            directory, ROOT / 'reports/model_artifacts.json', predictor.mode)
        report['messages'].extend(predictor.load_warnings)
    except Exception as exc:
        # Avoid exposing environment paths or private checkpoint contents.
        report['messages'].append('Readiness check failed: ' + type(exc).__name__ +
                                  '. Check dependencies with python -m pip check.')
    if not report['trained_ready']:
        nested = directory.exists() and any(p.parent != directory for p in directory.rglob('decision_policy.json'))
        report['messages'].append('Place decision_policy.json and a fitted model directly in checkpoints/.')
        if nested:
            report['messages'].append('A nested policy was found. Move artifact files out of the extra extracted folder.')
        report['messages'].append('The app can still run in capture-indicators-only mode; suitability will be uncertain.')
    elif not report['published_identity']['active_model_matches']:
        report['messages'].append('A fitted system is available, but its identity differs from or cannot be checked against the published evaluation.')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint-dir', type=Path)
    parser.add_argument('--output', type=Path, help='Optional JSON report; contains no images or case records')
    parser.add_argument('--require-trained', action='store_true', help='Exit 1 unless a fitted system loads')
    args = parser.parse_args()
    report = check_installation(args.checkpoint_dir)
    result = json.dumps(report, indent=2)
    print(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + '\n')
    raise SystemExit(1 if args.require_trained and not report['trained_ready'] else 0)


if __name__ == '__main__':
    main()
