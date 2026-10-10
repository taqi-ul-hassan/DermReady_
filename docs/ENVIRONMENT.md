# Environment setup

## Local CPU development

Target: Python 3.12, Linux x86_64. Other platforms must run the same checks before being called validated.

```bash
git clone https://github.com/taqi-ul-hassan/DermReady_.git
cd DermReady_
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell activation: .venv\Scripts\Activate.ps1
python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python -m pip check
python scripts/check_environment.py --output reports/environment_local.json
```

`requirements.txt` pins direct dependencies. `requirements-cpu.lock.txt` captures the complete tested Linux/Python 3.12 CPU environment. To reproduce the full snapshot, install it using PyPI plus the official CPU wheel index:

```bash
python -m pip install -r requirements-cpu.lock.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

The checker imports each dependency, runs MobileNetV3-Small with random weights on a synthetic image on CPU, checks OpenCV, and constructs a Gradio interface without publishing a server. It also checks CUDA when present. This is environment verification, not trained-model evaluation. No SCIN images or pretrained downloads are needed.

The application and inference modules are implemented. Real checkpoint loading and CPU prediction passed in step 10.

## Colab GPU and persistent storage

Open `notebooks/00_environment_setup.ipynb` in Colab. Select Runtime > Change runtime type and select an available GPU. Run cells in order:

1. Clone the public repository into the temporary runtime.
2. Keep Colab's bundled PyTorch/torchvision CUDA pair; install the pinned non-PyTorch dependencies.
3. Check dependency consistency and run the environment checker with `--require-gpu`.
4. Authorize the notebook's Google Drive mount with your own account.
5. Create and verify persistent directories under `MyDrive/DermReady`, generate a runtime config with absolute output paths, and write the runtime package snapshot to Drive.

Do not install the CPU lock file in Colab. If the preinstalled Torch pair cannot import or timm fails, use the official PyTorch selector for that runtime's Python/CUDA compatibility, restart the runtime, then rerun checks. Do not label Colab validated until the GPU check and Drive write check pass.

Datasets can be cached in the temporary runtime for speed. Checkpoints, split assignments, and experiment results should be written directly to the generated persistent paths. Training code must honor those paths when it is implemented. The notebook prepares persistence; it does not train or back up an existing model.

Google authorization and GPU allocation cannot be completed from a local terminal. Colab availability varies. CPU remains the development/demo fallback.

## References

- https://pytorch.org/get-started/locally/
- https://pytorch.org/get-started/previous-versions/
- https://research.google.com/colaboratory/faq.html
- https://colab.research.google.com/notebooks/io.ipynb

## Local validation result

Python 3.12.14: dependency consistency, all required imports, synthetic MobileNet CPU execution, OpenCV operation, and Gradio construction passed. See reports/environment_local.json. CUDA is unavailable in this local environment. Restricted CPU-topology detection required disabling the optional NNPACK backend in the checker. Pretrained download, trained checkpoint loading, and CPU prediction have since passed; see reports/steps_06_to_10.md.
