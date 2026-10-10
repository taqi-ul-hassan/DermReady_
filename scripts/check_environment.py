"""Verify dependencies and a synthetic CPU/GPU forward pass; no data/downloads."""
import argparse
import importlib
import importlib.metadata as metadata
import json
import platform
from pathlib import Path


def check_environment(require_gpu=False):
    packages = {'torch': 'torch', 'torchvision': 'torchvision', 'timm': 'timm',
                'pandas': 'pandas', 'numpy': 'numpy', 'Pillow': 'PIL',
                'opencv-python-headless': 'cv2', 'scikit-learn': 'sklearn',
                'matplotlib': 'matplotlib', 'gradio': 'gradio',
                'datasets': 'datasets', 'PyYAML': 'yaml', 'pytest': 'pytest',
                'socksio': 'socksio'}
    report = {'python': platform.python_version(), 'platform': platform.platform(),
              'packages': {}, 'errors': []}
    for distribution, module in packages.items():
        try:
            importlib.import_module(module)
            report['packages'][distribution] = metadata.version(distribution)
        except Exception as exc:
            report['errors'].append(f'{distribution}: {exc}')
    if not report['errors']:
        import torch
        import timm
        import cv2
        import numpy as np
        import gradio as gr
        torch.set_num_threads(2)
        # Restricted containers can hide CPU topology; avoid unsupported NNPACK.
        torch.backends.nnpack.set_flags(False)
        torch.manual_seed(42)
        model = timm.create_model('mobilenetv3_small_100', pretrained=False, num_classes=2).eval()
        with torch.inference_mode():
            output = model(torch.zeros(1, 3, 224, 224))
        assert output.shape == (1, 2) and torch.isfinite(output).all()
        report['cpu_forward_pass'] = 'passed (random weights; not a gradability prediction)'
        report['cuda_available'] = torch.cuda.is_available()
        if report['cuda_available']:
            with torch.inference_mode():
                output = model.cuda()(torch.zeros(1, 3, 224, 224, device='cuda'))
            assert output.shape == (1, 2) and torch.isfinite(output).all()
            report['gpu_forward_pass'] = 'passed'
            report['gpu_name'] = torch.cuda.get_device_name(0)
        elif require_gpu:
            report['errors'].append('GPU required but CUDA is unavailable')
        assert cv2.Laplacian(np.zeros((32, 32), dtype=np.uint8), cv2.CV_64F).shape == (32, 32)
        with gr.Blocks() as demo:
            gr.Markdown('Environment check only')
            gr.Image(type='pil')
        report['gradio_construction'] = 'passed (server not launched)'
    report['passed'] = not report['errors']
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-gpu', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = check_environment(args.require_gpu)
    except Exception as exc:
        report = {'passed': False, 'errors': [str(exc)]}
    result = json.dumps(report, indent=2)
    print(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + '\n')
    raise SystemExit(0 if report['passed'] else 1)

if __name__ == '__main__':
    main()
