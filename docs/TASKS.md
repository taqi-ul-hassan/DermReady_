# Implementation checklist

## Completed: steps 1 and 2
- [x] Define goal, target users, MVP, exclusions, and success criteria.
- [x] Choose a provisional case-level modeling and label policy.
- [x] Document single-image limitations and uncertainty requirements.
- [x] Initialize the supplied repository with files and tracked folder placeholders.
- [x] Add data/secrets/upload exclusions and code license.
- [x] Document references and remaining decisions.
- [ ] Verify current hackathon rules and deadline (external prerequisite).

## Step 3: environment
- [x] Create local Python 3.12 virtual environment, verify dependencies, and pin compatible versions.
- [x] Save full CPU lock snapshot, environment report, and repeatable checker.
- [x] Prepare Colab notebook with GPU checks and persistent Drive output configuration.
- [ ] Run Colab notebook with a signed-in account; confirm GPU execution and Drive write test.
- [x] Verify synthetic MobileNet CPU execution, OpenCV, and Gradio construction.
- [ ] Verify real checkpoint loading/CPU inference after model implementation.

## Step 4: data audit
- [ ] Read current SCIN schema, license, and sample records.
- [ ] Verify label unit, fields, images, missingness, and disagreement.
- [ ] Write reports/data_audit.md; decide go/no-go at hour 2.

## Step 5: labels and splits
- [ ] Implement and validate consensus policy.
- [ ] Build local manifests preserving case IDs and label provenance.
- [ ] Save case-level train/validation/test splits; check overlap and duplicates.

## Steps 6 and 7: preprocessing and baseline
- [ ] Validate uploads, correct orientation, preserve originals.
- [ ] Implement model transforms and training-only augmentation.
- [ ] Compute blur, exposure, contrast, and resolution.
- [ ] Tune baseline rules on validation data; save baseline metrics.

## Step 8: model
- [ ] Implement MobileNet and documented case aggregation.
- [ ] Run a small pipeline check, train, and save best validation checkpoint.
- [ ] Verify standalone prediction and compare baseline; decide fallback at hour 12.

## Steps 9 and 10: decision policy and UI
- [ ] Select two validation thresholds and report uncertainty coverage.
- [ ] Implement supported feedback, qualified outputs, and warning text.
- [ ] Build and integrate Gradio; verify upload retention/cache behavior.

## Steps 11 and 12: evaluation
- [ ] Freeze policy and evaluate held-out cases and single-image behavior.
- [ ] Save confusion matrix, ungradable recall, false acceptance/rejection, F1, balanced accuracy.
- [ ] Define denominators for three-state metrics and report coverage.
- [ ] Evaluate at least two controlled degradations and save plots.
- [ ] Review errors and limitations.

## Optional after MVP
- [ ] Feature classifier, Grad-CAM, adequate-sample subgroup analysis, multi-image UI.

## Steps 14 and 15: delivery
- [ ] Test grouped splits, preprocessing, thresholds, invalid files, and CPU behavior.
- [ ] Finish reproduction instructions, citations, results, and limitations.
- [ ] Reproduce from a fresh environment and inspect tracked files.
- [ ] Prepare permitted examples, demo, screenshots, and backup recording.
- [ ] Confirm current submission requirements and submit.
