# DermReady

Image-suitability quality gate for dermatology photography.

> Research prototype only; not a diagnosis or substitute for medical advice. Results cannot guarantee clinical adequacy. Follow your clinician's instructions.

## Status

Steps 1–14 are implemented (final presentation/submission excluded): repository, environments, SCIN audit, saved grouped splits, preprocessing, quality baseline, pretrained MobileNet training, validation-selected three-state policies, and a working local Gradio app.

The default is the quality-feature baseline because the full guarded validation policy had fewer false acceptances. A trained MobileNet option is available. Validation performance is weak, single-image labels are case-derived proxies, and clinical adequacy is not established. The frozen held-out evaluation is complete on 107 cases; test results did not alter training, thresholds, or the default model. The default single-image pipeline had 1/23 weak-proxy false acceptances, 25/84 false rejections, and 61/107 uncertain outputs. See [held-out evaluation](reports/heldout_test.md). Controlled blur and lighting stress tests are complete; see [robustness results](reports/robustness.md).

See [steps 6–10 report](reports/steps_06_to_10.md), [data audit](reports/data_audit.md), and [split summary](reports/split_summary.md).

## Run the app

### Check → capture again → compare

DermReady now offers a capture-review workflow: inspect an original, follow the prioritized next action, then compare it with a newly captured photograph. The comparison shows focus, exposure, clipping and contrast changes with side-by-side previews. It does not alter photographs or claim clinical improvement. Permitted synthetic examples are available in the app, and the evidence panel shows frozen error rates alongside decision coverage and uncertainty.

The active mode is visible immediately. A public checkout without private fitted artifacts supports capture indicators and comparison; learned suitability decisions require the artifact bundle. See [demo guide](docs/DEMO_GUIDE.md) and [submission draft](docs/SUBMISSION_DRAFT.md).

Place best.pt, quality_baseline.json, and decision_policy.json from the private trained-artifact bundle in checkpoints/. Then:

```bash
python app.py
# Optional MobileNet path:
python app.py --model cnn
```

Open http://127.0.0.1:7860. Without fitted artifacts the app starts in explicitly labeled features-only mode and returns uncertain.
See [Windows quick start](docs/WINDOWS_QUICKSTART.md), [run guide](docs/RUN_APP.md), [reproduction guide](docs/REPRODUCIBILITY.md), and [model card](docs/MODEL_CARD.md). Double-click launch_windows.bat after installing dependencies. The [Colab training notebook](https://colab.research.google.com/github/taqi-ul-hassan/DermReady_/blob/main/notebooks/03_train_and_prepare_demo.ipynb) writes private artifacts to your Drive and does not publish a share link.

## Goal and target users

Help a person preparing photographs for remote dermatology review identify potentially correctable capture problems before submission. A clinician or service remains responsible for clinical review.

## MVP

- Upload one photograph through a Gradio interface.
- Return **likely suitable for review**, **may need a retake**, or **uncertain**.
- Display blur, exposure/brightness, contrast, and resolution indicators.
- Offer non-diagnostic capture guidance supported by those indicators.
- Display the research-only notice.
- Provide reproducible held-out evaluation and documented limitations.

## Two separate tasks

1. Estimate dermatologist-assessed **case/image-set gradability** using SCIN labels.
2. Measure capture-quality proxies and evaluate controlled degradations.

SCIN ungradable labels can reflect insufficient information, multiple conditions, no discernible pathology, or image quality. They are not ground truth for blur or poor lighting.

## Modeling decision

Use case-level supervision and splitting. Preserve all image references and label provenance for each case. The feature baseline aggregates per-image capture measures; the CNN averages per-image embeddings before case classification. Both use case-level supervision.

The MVP accepts a single image, which is less information than a multi-image case. Any score from that input must be described as a limited single-image estimate from a case-trained system and evaluated separately. Do not silently copy case labels onto images as definitive image-level labels.

Audited consensus policy: explicitly map the two unambiguous categorical values; exclude no-discernible-pathology votes, missing votes, ties, and cases with fewer than two valid votes; stop on unknown categorical values. This retains 710 cases before missing-image handling. See reports/data_audit.md for the mapping and cohort selection limits. Cases connected by shared image paths or known content hashes remain in one split. The saved splits contain 497 training, 106 validation, and 107 test cases.

## Success criteria

- Dataset schema and terms reviewed; provenance recorded.
- Saved train/validation/test splits contain no overlapping case IDs.
- A learned model or honestly labeled quality-feature baseline runs end to end.
- Held-out results include ungradable recall, false acceptance, false rejection, confusion matrix, and uncertain-output coverage.
- At least two controlled degradation types evaluated.
- All three UI states and supported feedback work.
- Setup and evaluation can be reproduced; demo and backup recording ready.

Thresholds and any numeric performance target will be set using validation data and documented before test evaluation. There is no clinically validated threshold.

## Scope

Required: lightweight baseline, image-quality features, three-state feedback, Gradio demo, evaluation report.
Optional after MVP: feature classifier, Grad-CAM, subgroup analysis with adequate counts, additional corruptions, multi-image upload.
Excluded: disease diagnosis, cancer screening, clinical deployment, EHR integration, mobile app, generative enhancement in the decision pipeline.

## Repository layout

| Path | Responsibility |
| --- | --- |
| app.py | Working local Gradio entry point |
| configs/experiment.yaml | Provisional experiment settings |
| src/data_loader.py | Cases and explicit label parsing |
| src/splits.py | Connected groups, assignment, leakage verification |
| scripts/prepare_scin.py | Private manifests and reproducible split files |
| src/preprocessing.py | Upload validation and transforms |
| src/quality_features.py | Capture-quality proxies |
| src/model.py | Classifier and case aggregation |
| src/train.py | Training and checkpointing |
| src/evaluate.py | Held-out metrics |
| src/inference.py | Model loading and predictions |
| src/feedback.py | States and supported retake guidance |
| src/perturbations.py | Controlled stress tests |
| src/explain.py | Optional model visualization |
| notebooks/ | Executable setup, audit, split, and training notebooks |
| tests/ | 34 automated checks; trained round-trip requires private artifacts |
| data/ | Local dataset and split artifacts |
| checkpoints/ | Local model files |
| reports/ | Audit, aggregate metrics, figures |
| assets/demo/ | Permitted public examples only |
| docs/ | Scope, task list, data/privacy notes |

## Environment setup

See [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) for local CPU installation and full-lock reproduction.
The tested Linux/Python 3.12 snapshot is in requirements-cpu.lock.txt. Direct dependencies are pinned in requirements.txt.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python -m pip check
python scripts/check_environment.py
```

[Open the environment notebook in Colab](https://colab.research.google.com/github/taqi-ul-hassan/DermReady_/blob/main/notebooks/00_environment_setup.ipynb).
It checks CUDA and prepares persistent Google Drive output directories. Do not install the CPU lock file in Colab.
The user reports completing Colab setup; live outputs were not independently inspected. Real CPU checkpoint inference has passed. The app runs locally; trained artifacts are kept outside public Git.

## Data, privacy, and license

SCIN has separate data-use terms; the code license does not license dataset images, labels, or pretrained weights. The current official terms were reviewed for this audit; see docs/SCIN_USAGE.md and recheck before sharing material.
Do not commit dataset images, case manifests, model weights, credentials, or private uploads.
Uploads are not added to datasets/logs. Gradio temporary upload/preview files are configured for periodic cleanup; public hosting/cache behavior remains unverified.
Only explicitly permitted examples belong in assets/demo.

## Sources to verify before implementation

- [SCIN repository](https://github.com/google-research-datasets/scin)
- [SCIN schema](https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md)
- [SCIN Data Use License](https://github.com/google-research-datasets/scin/blob/main/LICENSE)
- [SCIN dataset viewer](https://huggingface.co/datasets/google/scin)
- [Banana Hacks FAQ](https://www.bananahacks.tech/faq)
- [Banana Hacks code of conduct](https://www.bananahacks.tech/code-of-conduct)

Official event rules were reviewed; deadline sources conflict. See docs/EVENT_RULES.md. User eligibility and the announced challenge/theme are not independently verified.

## Model and library attribution

- [timm / Ross Wightman](https://github.com/huggingface/pytorch-image-models), Apache 2.0.
- [Pretrained MobileNetV3-Small model card](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k), ImageNet-1k initialization, Apache 2.0 model-card license. DermReady adds a trained case head; later backbone fine-tuning was not selected.
- [PyTorch](https://pytorch.org/), [torchvision](https://github.com/pytorch/vision), [OpenCV](https://opencv.org/), [scikit-learn](https://scikit-learn.org/), [Pillow](https://python-pillow.github.io/), [Gradio](https://www.gradio.app/). See requirements files for all dependencies.
- SCIN and Ward et al.: attribution and separate data terms in docs/SCIN_USAGE.md.
- AI coding/documentation assistance: ChatGPT/Codex.
