# Implementation checklist

## Completed: steps 1 and 2
- [x] Define goal, target users, MVP, exclusions, and success criteria.
- [x] Choose a provisional case-level modeling and label policy.
- [x] Document single-image limitations and uncertainty requirements.
- [x] Initialize the supplied repository with files and tracked folder placeholders.
- [x] Add data/secrets/upload exclusions and code license.
- [x] Document references and remaining decisions.
- [x] Review official event rules; document conflicting deadline sources in docs/EVENT_RULES.md.

## Step 3: environment
- [x] Create local Python 3.12 virtual environment, verify dependencies, and pin compatible versions.
- [x] Save full CPU lock snapshot, environment report, and repeatable checker.
- [x] Prepare Colab notebook with GPU checks and persistent Drive output configuration.
- [x] User reports completing Colab setup notebook; remote outputs not independently inspected.
- [x] Verify synthetic MobileNet CPU execution, OpenCV, and Gradio construction.
- [x] Verify real checkpoint loading and CPU inference.

## Step 4: data audit
- [x] Read current SCIN schema, license, and sample records.
- [x] Verify label unit, fields, images, missingness, and disagreement.
- [x] Write reports/data_audit.md; decide go/no-go at hour 2.

## Step 5: labels and splits
- [x] Implement and validate consensus policy.
- [x] Build local manifests preserving case IDs and label provenance.
- [x] Save splits grouped by connected cases/shared image paths; handle missing objects, then check case/image overlap.

## Steps 6 and 7: preprocessing and baseline
- [x] Validate uploads, correct orientation, preserve originals.
- [x] Implement model transforms and training-only augmentation.
- [x] Compute blur, exposure, contrast, and resolution.
- [x] Tune baseline rules on validation data; save baseline metrics.

## Step 8: model
- [x] Implement MobileNet and documented case aggregation.
- [x] Run a small pipeline check, train, and save best validation checkpoint.
- [x] Verify standalone prediction and compare baseline; decide fallback at hour 12.

## Steps 9 and 10: decision policy and UI
- [x] Select two validation thresholds and report uncertainty coverage.
- [x] Implement supported feedback, qualified outputs, and warning text.
- [x] Build/integrate local Gradio, verify upload API and private-path blocking, configure temporary-cache cleanup.
- [ ] Verify external hosting retention/cache behavior before public deployment (not part of local MVP).

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
