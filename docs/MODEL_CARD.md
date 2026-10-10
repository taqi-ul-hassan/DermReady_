# DermReady model and policy card

## Intended use

Research demonstration of capture indicators and case-derived gradability estimates for dermatology photography. Single-image uploads receive likely suitable for review, may need a retake, or uncertain, plus qualified guidance. A clinician must determine adequacy. This system does not diagnose, screen for cancer, assess urgency, or guarantee clinical suitability.

## Data and supervision

SCIN release 1.0.0, attributed to Ward et al., JAMA Network Open 2024, e2446615, DOI 10.1001/jamanetworkopen.2024.46615. Separate SCIN data terms apply; see SCIN_USAGE.md. Strict consensus requires at least two unambiguous reviewer votes and a non-tied majority. Missing and no-discernible-pathology votes are excluded. The retained cohort is 710 cases, substantially smaller than the 5,033-case source.

Cases connected through shared paths or known MD5 hashes are grouped, including links through excluded cases. Split seed 42 produces 497 train, 106 validation and 107 test cases. Counts of ungradable cases are 107, 23 and 23 respectively. Audits and hashes are recorded in reports/data_audit.json and reports/split_summary.json. No skin tone, demographic, or disease features are used by the models; subgroup performance has not been established.

## Models

- Default: class-balanced logistic regression over 25 aggregate focus, exposure, contrast, resolution, aspect ratio and image-count features. Standardization and classifier parameters are fitted on training cases only; deployment uses JSON parameters.
- Optional CNN: timm mobilenetv3_small_100.lamb_in1k, ImageNet initialization, mean image embeddings per case, two-class trained head. One head-warmup epoch and two fine-tuning epochs were run. Validation selected epoch 1; the deployed encoder therefore retains pretrained weights with a trained case head.
- Preprocessing: orientation correction, RGB conversion, whole-image 224-pixel letterbox and ImageNet normalization. Horizontal flips are training-only. Upload guards reject corrupt, animated, oversized, or extreme inputs. Unsupported modes/extremes and capture flags restrict acceptance. These are not validated skin or framing detectors.

## Decision policy

Thresholds and default model were selected only on the 106-case validation set using first-listed single images and inherited case labels as weak proxies. Scores are uncalibrated research values, not clinical probabilities. Capture flags block suitable outputs. The default baseline was selected before held-out evaluation; it remains unchanged afterward. See reports/decision_policy.json for exact thresholds and selection rules.

## Frozen held-out results

107 cases / 299 images, with unchanged artifact and split hashes. All-image case balanced accuracy: baseline 0.672, CNN 0.602; ROC-AUC: baseline 0.645, CNN 0.701. These binary case results are separate from the app's three-state policy.

The default single-image pipeline returned 12 suitable, 34 retake and 61 uncertain outputs. Against weak case-label proxies it falsely accepted 1/23 ungradable cases (4.3%; Wilson 95% 0.8–21.0%) and requested retakes for 25/84 gradable cases (29.8%; 95% 21.0–40.2%). Decision coverage was 43.0%. These small-sample results do not demonstrate clinical safety.

Controlled blur, darkening and brightening removed all baseline suitable outputs; CNN retained two under mild blur. Edited images have no new clinical labels: these are paired sensitivity experiments, not clinical accuracy. Full metrics/denominators appear in reports/heldout_test.md and reports/robustness.md.

## Limitations and foreseeable errors

Case labels can reflect clinical information sufficiency rather than a correctable camera defect. A single image contains less information than a case image set. Retakes may be unnecessary, and a clear image may still be inadequate. The strict consensus subset may not represent routine uploads. Real camera shifts, outside-source images, framing, body region, skin tone, age, device, and clinical population coverage have not been validated. No individual fairness or subgroup assurance is claimed.

The same validation data selected thresholds and model: validation figures are optimistic. The final test set is now consumed for reporting and cannot support further model/policy selection; new independent data are required for revisions. Six test images were decoded for readability before splitting, with no training or threshold use.

## Privacy and deployment

App binds to localhost. It does not append uploads to training data or logs. Gradio creates temporary upload/preview files; cleanup is periodic, not immediate deletion. Browser/proxy caches may persist. No public deployment or external-host retention validation was performed. Models and dataset records remain outside public Git; synthetic demo assets contain no patients. See DATA_AND_PRIVACY.md and RUN_APP.md.

## Attribution and maintenance

Original code: MIT. timm/MobileNet initialization: Ross Wightman / timm, Apache 2.0. Dependencies and dataset sources are linked in README. ChatGPT/Codex assisted implementation and documentation. Evaluation/version provenance is stored in reports/test_freeze.json and reports/robustness_protocol.json. Change the scientific policy only with separate independent evaluation.
