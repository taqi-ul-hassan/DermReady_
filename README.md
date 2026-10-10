# DermReady

Image-suitability quality gate for dermatology photography.

> Research prototype only; not a diagnosis or substitute for medical advice. Results cannot guarantee clinical adequacy. Follow your clinician's instructions.

## Status

Project scope and repository scaffold are established. Local Python 3.12 CPU dependencies are installed, pinned, and smoke-tested. The user reports completing the Colab setup notebook; its remote outputs have not been inspected here.
SCIN data access and audit are complete. Splits, training, evaluation, and the Gradio app are not implemented. See [data audit](reports/data_audit.md).
No performance or clinical-benefit claims have been established.

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

Use case-level supervision and splitting. Preserve all image references and label provenance for each case. The planned baseline extracts per-image representations and aggregates them at case level; the implementation must be validated after schema inspection.

The MVP accepts a single image, which is less information than a multi-image case. Any score from that input must be described as a limited single-image estimate from a case-trained system and evaluated separately. Do not silently copy case labels onto images as definitive image-level labels.

Audited consensus policy: explicitly map the two unambiguous categorical values; exclude no-discernible-pathology votes, missing votes, unknown values, ties, and cases with fewer than two valid votes. This retains 710 cases before missing-image handling. See reports/data_audit.md for the mapping and cohort selection limits. Cases connected by shared image paths must also remain in one split.

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
| app.py | Future Gradio entry point |
| configs/experiment.yaml | Provisional experiment settings |
| src/data_loader.py | Cases, label policy, grouped splits |
| src/preprocessing.py | Upload validation and transforms |
| src/quality_features.py | Capture-quality proxies |
| src/model.py | Classifier and case aggregation |
| src/train.py | Training and checkpointing |
| src/evaluate.py | Held-out metrics |
| src/inference.py | Model loading and predictions |
| src/feedback.py | States and supported retake guidance |
| src/perturbations.py | Controlled stress tests |
| src/explain.py | Optional model visualization |
| notebooks/ | Future exploration notebooks |
| tests/ | Future meaningful checks |
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
The user reports completing Colab setup; live outputs were not independently inspected. Trained-model inference remains pending. The app is not implemented yet.

## Data, privacy, and license

SCIN has separate data-use terms; the code license does not license dataset images, labels, or pretrained weights. The current official terms were reviewed for this audit; see docs/SCIN_USAGE.md and recheck before sharing material.
Do not commit dataset images, case manifests, model weights, credentials, or private uploads.
The intended upload policy is no unnecessary retention; hosting/cache behavior must be verified before a public demo.
Only explicitly permitted examples belong in assets/demo.

## Sources to verify before implementation

- [SCIN repository](https://github.com/google-research-datasets/scin)
- [SCIN schema](https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md)
- [SCIN Data Use License](https://github.com/google-research-datasets/scin/blob/main/LICENSE)
- [SCIN dataset viewer](https://huggingface.co/datasets/google/scin)
- [Banana Hacks FAQ](https://www.bananahacks.tech/faq)
- [Banana Hacks code of conduct](https://www.bananahacks.tech/code-of-conduct)

Event deadline, eligibility, hacking window, and submission requirements are unverified. Record confirmed rules in docs/PROJECT_SCOPE.md before relying on them.
