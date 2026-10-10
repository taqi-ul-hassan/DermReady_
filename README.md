# DermReady

Image-suitability quality gate for dermatology photography.

> Research prototype only; not a diagnosis or substitute for medical advice. Results cannot guarantee clinical adequacy. Follow your clinician's instructions.

## Status

Steps 1 and 2 are complete: project scope and repository scaffold.
Data access, label review, training, evaluation, and the Gradio app are not implemented.
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

Provisional consensus policy: majority vote with at least two available dermatologist votes; exclude unresolved ties and insufficient votes from supervised training, retain them for audit. Confirm the actual schema before finalizing this policy.

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

## Future environment setup

Dependencies are provisional and unpinned until tested in the actual local/Colab environment. This scaffold does not launch a functional app.

```bash
git clone https://github.com/taqi-ul-hassan/DermReady_.git
cd DermReady_
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell alternative: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

Copy .env.example to .env only if environment variables are needed. No credentials are currently required. See docs/TASKS.md for the implementation order.

## Data, privacy, and license

SCIN has separate data-use terms; the code license does not license dataset images, labels, or pretrained weights. Review current terms before downloading or sharing.
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
