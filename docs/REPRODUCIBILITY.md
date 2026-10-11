# Reproduce DermReady

## Run the existing trained demo

See WINDOWS_QUICKSTART.md or ENVIRONMENT.md. The private trained-artifact bundle supplies best.pt, quality_baseline.json and decision_policy.json; copy them directly into checkpoints/. The public repository intentionally contains no trained weights or SCIN patient images. Starting the app with those artifacts requires no runtime pretrained-model download.

## Recreate the scientific pipeline

Use a fresh Linux/Python 3.12 CPU environment or the prepared Colab notebooks. CPU lock reproduction uses requirements-cpu.lock.txt with the official PyTorch CPU index. Colab keeps its bundled compatible CUDA Torch/torchvision pair and installs requirements-colab.txt.

From the repository root:

```bash
python scripts/audit_scin.py --help
python scripts/prepare_scin.py --help
python scripts/audit_scin.py
python scripts/prepare_scin.py
python scripts/cache_images.py
python scripts/quality_baseline.py
python -m src.train --config configs/experiment.yaml
python scripts/select_policy.py
python -m pytest -q
python scripts/evaluate_test.py
python scripts/evaluate_robustness.py
python app.py
```

Audit and split preparation use the official SCIN release, with hashes recorded. The default preprocessing cache fetches only train/validation; evaluate_test.py explicitly accesses the held-out test cache. The first training run also downloads ImageNet initialization from timm's model source. Keep data/raw, data/processed, data/splits and checkpoints private. See each script's --help to change output paths; Colab notebooks provide persistent Drive locations.

Do not expect a fresh retraining run to produce byte-identical floating-point weights across OS, CPU/GPU, libraries or hardware. The seed/splits and label policy are deterministic; final reports identify exact evaluated weights with SHA-256. To reproduce the published evaluation, use the supplied frozen artifact bundle with matching private manifests/splits. Changing weights or policy constitutes a new experiment, requiring independent final evaluation rather than tuning on this consumed test set.

Final evaluation scripts refuse to overwrite an existing report. Rerun a frozen experiment in a fresh output/workspace directory. The scientific outputs are reports/heldout_test.json, reports/test_freeze.json and reports/robustness.json; per-case predictions are private.

## Fresh-environment validation performed

A separate workspace and genuinely new virtual environment installed the complete CPU lock from package indexes. No existing site-packages were inherited. The dependency consistency check, all 30 tests, environment imports, synthetic MobileNet CPU forward, real trained-artifact round trips, Gradio construction and a local HTTP upload/private-path-blocking smoke test passed. Test records/data were not copied to this validation workspace; a synthetic private-file marker exercised HTTP blocking.

This checks installation and app reproduction with frozen artifacts, not a second training run or independent replication of the scientific study. Linux/Python 3.12 is maintainer-tested. The user reported a working Windows setup; Windows automated execution and public hosting are not claimed. The GitHub Actions CPU workflow is configured; its remote execution has not been inspected.


## Evaluation integrity checks added during project review

New final evaluations verify cases.jsonl, images.csv, assignments and each split against private splits/provenance.json, then check source CSV/inventory hashes, case labels, group IDs, image counts and cross-split image/group leakage before downloading or evaluating images. The freeze additionally records manifest/provenance hashes. Robustness evaluation uses the same verified cohort and checks its split hashes against the final freeze.

These checks protect future runs; they are not a rerun of the published experiment. Keep existing final reports. For a new experiment use separate private checkpoint, processed, split and report directories through the scripts' CLI arguments. Do not overwrite frozen artifacts or tune on the consumed test cohort. Public report paths already contain final results, so evaluation intentionally refuses to overwrite them.
