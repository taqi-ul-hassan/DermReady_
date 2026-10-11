# Run DermReady

## Local demo with trained artifacts

Activate the environment documented in ENVIRONMENT.md. Place the trained artifact bundle's best.pt, quality_baseline.json, and decision_policy.json under checkpoints/. Keep that folder out of Git.

```bash
python app.py
# Optional trained image model instead of the default feature baseline:
python app.py --model cnn
# Alternate private checkpoint folder:
python app.py --checkpoint-dir /absolute/path/to/checkpoints
```

Open http://127.0.0.1:7860. Upload one PNG, JPEG, or still WebP photograph and choose Check photograph. Use Clear photograph to reset the displayed result.

Without trained artifacts the app still starts, measures capture indicators, and returns uncertain with an explicit features-only notice. It never presents a randomly initialized model as trained.

## Reproduce steps 6–10

After the audit and split preparation:

```bash
python scripts/cache_images.py
python scripts/quality_baseline.py
python -m src.train --config configs/experiment.yaml
python scripts/select_policy.py
python -m pytest tests -q
python app.py
```

The default cache script downloads/decode-checks TRAIN and VALIDATION images only. It does not fetch test images. Do not tune the model or thresholds on the test split.

For Colab, use notebooks/03_train_and_prepare_demo.ipynb after the environment notebook. It stores fitted artifacts and reports in your own Drive. No public Gradio share link is created automatically. Download the resulting artifacts to run the local app.

## Current system

The default is the quality-feature logistic-regression baseline because its full guarded validation policy made fewer false acceptances. The trained MobileNet option remains available. One epoch of head warmup plus two backbone fine-tuning epochs were completed; the warmup checkpoint was selected because later fine-tuning performed worse on validation.

All three states are supported. Capture flags block acceptance, and unsupported modes or near-constant images or out-of-reference high-frequency texture are uncertain. These checks are not a validated detector for unrelated images. Model scores are uncalibrated and must not be described as probabilities of clinical adequacy.

## Upload handling

The application does not append uploads to its dataset, write image records to logs, or save them as examples. Gradio does create temporary upload and preview files. Cleanup is configured to scan every 30 seconds and delete files older than 60 seconds; this is not a promise of instant deletion or removal from a browser/proxy cache. Clear resets the view. No public examples, flagging, analytics, run history, or public share link are enabled.

Local startup binds to 127.0.0.1, enforces a 20 MB upload limit, and blocks serving data/, checkpoints/, and .env. The local HTTP smoke test verified that a private dataset file could not be served. Public deployment would require a separate review of hosting caches, logs, access controls, retention, and permitted examples; no public deployment was performed.

## Meaning and limits

SCIN supervision is case-level. The single-image policy was selected using one fixed first-listed image per validation case with its case label as weak supervision. No true image-level clinical adequacy labels were obtained. Quality measures use focus, exposure, contrast, and resolution proxies; no anatomical framing detector is implemented.

Research prototype only; not a diagnosis or substitute for medical advice. Follow your clinician's instructions. Frozen final test evaluation is complete: see ../reports/heldout_test.md. Controlled blur/lighting experiments are complete in reports/robustness.md. Subgroup assurance is not established. The final presentation/demo recording and submission are left to the user.

## Step 11: held-out evaluation

After preparing private manifests and frozen artifacts, run `python scripts/evaluate_test.py`. The report records artifact/split hashes, all-image case metrics, and the unchanged single-image app policy. It refuses to overwrite an existing final report. Demo-only installations do not contain the private manifests and do not need to rerun evaluation. See [results](../reports/heldout_test.md).

## Finished delivery materials

See [Windows quick start](WINDOWS_QUICKSTART.md), [reproduction](REPRODUCIBILITY.md), [model card](MODEL_CARD.md), and [demo guide](DEMO_GUIDE.md). Synthetic assets in assets/demo/ contain no patient photographs. Screenshots/final recording are part of the excluded presentation step; no public app hosting was performed.


## Verify the installation

From the folder containing app.py, run:

```powershell
.\.venv\Scripts\python.exe scripts/check_installation.py --require-trained
```

The checker shows the active system, missing or nested artifact files, and whether the active model/policy match the published hashes. It does not download weights or read medical images. Without `--require-trained`, it also reports a capture-indicators-only installation. A fitted but different artifact may run; historical performance must not be attributed to it.
