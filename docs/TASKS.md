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
- [x] Freeze policy and evaluate held-out cases and single-image behavior.
- [x] Save confusion matrix, ungradable recall, false acceptance/rejection, F1, balanced accuracy.
- [x] Define denominators for three-state metrics and report coverage.
- [x] Evaluate blur and two lighting degradations on frozen held-out inputs; save plots.
- [x] Review held-out errors and limitations (reports/heldout_test.md); degradation analysis completed in reports/robustness.md.

## Optional after MVP
- [ ] Grad-CAM, adequate-sample subgroup analysis, multi-image UI. The feature classifier is implemented.

## Step 13: technical review
- [x] Record model card, supervision limits, error review, provenance and licenses.
- [x] Keep models, thresholds and default unchanged after final tests.

## Step 14: delivery checks
- [x] Test grouped splits, preprocessing, thresholds, invalid files, and CPU behavior.
- [x] Finish reproduction instructions, citations, results, and limitations.
- [x] Install CPU lock in a new environment; test trained artifacts/API; inspect publication allowlist.
- [x] Prepare original synthetic examples, demo guide, result plots, and Windows launch helpers.
- [x] Recheck published submission requirements and record persistent deadline conflict.

## Step 15: final presentation — excluded by user
- [ ] Capture final screenshots and presentation/demo recording.
- [ ] Create final presentation and complete official portal submission.

Screenshot capture was unavailable: the cloud browser could not reach the workspace local app. No fabricated screenshots or recording are supplied. The local app/API passed fresh-environment tests. Optional research enhancements and external hosting remain outside the requested local MVP.
