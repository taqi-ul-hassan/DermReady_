# Technical and bias review

## Outcome

The app is a functioning research capture-review prototype. The available results do **not** establish accurate clinical suitability decisions for every dermatology image or equal performance across populations. A frontend fix cannot supply missing clinical labels or broader independent validation.

This update fixes stale-result handling, explains the actual cause of each decision, validates model artifact structures, removes the large notice below the hero as requested, increases review text size, and moves the evidence chart title above the image. The notice remains in Evidence & limits, and the research-prototype badge remains in the hero. No trained weights or frozen thresholds are changed.

## Why uncertain is common

The baseline retake threshold is 0.673427 and its acceptance threshold is 0.920448. Scores between them yield uncertain. An acceptance-band score is also uncertain if capture guards fire. Near-uniform images, out-of-reference texture, unsupported original color modes, composited transparency, extreme aspect ratios and unavailable fitted artifacts/policies are separate uncertainty reasons.

These uncalibrated scores are **not** probabilities of clinical adequacy. A score of 0.8 does not mean 80% clinically suitable. Validation threshold selection was designed to limit empirical false acceptance on only 23 ungradable validation cases; it therefore leaves a wide uncertainty band. Eight of the baseline's 21 validation score-band suitable outputs were blocked by capture guards, leaving 13 suitable outputs. The published test report does not contain the per-image scores/features needed to decompose its uncertainty by guard; the app now explains the reason for each live result.

The unchanged held-out baseline returned 12 suitable, 34 retake and 61 uncertain results out of 107. This is a 57.0% uncertainty rate, not evidence of a software crash. Reducing uncertainty by lowering the threshold would change the scientific policy and requires new independent validation; the consumed final test set must not select the new threshold.

## Available class-conditional check

| Case label (weak proxy for a single image) | Retake | Uncertain | Suitable | Uncertainty rate |
| --- | ---: | ---: | ---: | ---: |
| Ungradable, n=23 | 9 | 13 | 1 | 56.5% |
| Gradable, n=84 | 25 | 48 | 11 | 57.1% |

The similar uncertainty rates do not establish demographic fairness. The default policy falsely accepted 1/23 ungradable cases and requested retakes for 25/84 gradable cases. Its 1/23 false-acceptance rate has a wide 95% interval of 0.8–21.0%. The all-image case balanced accuracy is 0.672; this is separate from the single-image app policy. The CNN did not demonstrate universally accurate performance either.

## Bias and generalization risks

- **Source population:** SCIN is a voluntary dataset collected from US internet users. Its authors report higher representation of women and younger individuals. Those source figures cannot be assumed to describe DermReady's selected subset or another country.
- **Selection:** strict multi-reviewer consensus retains 710/5,033 cases (14.1%). The retained cohort has 557 gradable and 153 ungradable cases. Selection for reviewer availability/agreement can change population and condition distributions.
- **Label mismatch:** SCIN gradability is assessed for a case/image set and can reflect insufficient clinical information or multiple conditions. One uploaded photograph inherits a case label only as a weak evaluation proxy. A technically clear photograph can still have an ungradable case label; a retake may not resolve the information gap.
- **Capture proxies:** brightness, clipped-pixel fractions, focus and contrast depend on lighting, background, skin appearance, texture, framing and resolution. The brightness guards were based on validation quantiles, not dermatologist-labeled exposure defects. They could produce different decisions across skin tones or capture settings. This is a risk inference, not a measured disparity. Guidance now asks users to inspect visible detail rather than declaring that low brightness proves underexposure.
- **Missing demographics:** SCIN demographic fields are optional; image-estimated skin-type/tone labels have measurement limits. Neither demographic subgroup predictions nor a joined private outcome table were available in this review workspace. No skin-tone, age, sex, ethnicity, device, body-site or condition-specific performance comparison was performed. This audit cannot declare those groups unbiased.
- **Outside-source inputs:** dermoscopic, histology, pediatric, clinical-system and other outside-source images have no separate validation. Palette/grayscale/CMYK originals, alpha-composited images and extreme aspect ratios intentionally receive uncertain under the frozen rules. Supported PNG/JPEG/still-WebP decoding does not mean validated performance on every kind of image.
- **Content coverage:** no validated skin detector or anatomical framing model exists. Unrelated images can still resemble the training features; the high-texture guard is not a general unrelated-image detector.

## Technical fixes and verification

Changed uploads and either retake-comparison input now clear previous previews, tables, assessment and guidance. A per-browser-session revision gate suppresses an in-flight function's output when its review has been invalidated before completion. The gate stores only a revision counter, not photographs; browser sessions are independent. This does not claim a browser/network-level transactional guarantee.

Policy JSON and feature-baseline structure now require valid supported model bands, finite arrays, positive scales and matching feature columns. Invalid artifacts fall back to capture indicators with a visible explanation instead of producing unsupported scores or crashing startup. Valid frozen artifact semantics are preserved.

Decision explanations distinguish an intermediate score, a capture guard, unsupported color/geometry, near-uniform content and unavailable artifacts. Regression tests compare the decision states with the previous frozen rules over 200 generated cases. A separate test checks the saved policy remains unchanged. Scope and live-upload API tests are recorded in reports/technical_bias_audit_checks.json.

The private trained checkpoints were not available in this fresh review workspace; their round-trip test is skipped. No retraining or new clinical accuracy improvement is claimed.

## What is needed for stronger accuracy and fairness evidence

Collect independently labeled **image-level suitability and capture-defect** outcomes for the intended use, with appropriate consent and meaningful coverage of skin tones, ages, body sites, conditions, camera settings and clinical versus consumer images. Keep independent development, validation and final evaluation cohorts; report subgroup denominators, false acceptance/rejection, uncertainty and intervals, including missing demographic categories. Use sufficient subgroup sample sizes and separate outside-source testing. Adjust models or thresholds only on development/validation data, then test the new policy independently. Do not infer demographics from a user's live photograph or claim universal accuracy from aggregate results.

## Primary sources reviewed

- SCIN official dataset/schema: https://github.com/google-research-datasets/scin and https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md
- Google Research's SCIN description, March 19, 2024: https://research.google/blog/scin-a-new-resource-for-representative-dermatology-images/
- Original study: Ward et al., JAMA Network Open, 2024;7:e2446615, DOI 10.1001/jamanetworkopen.2024.46615: https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2826506
- Gradio File events: https://www.gradio.app/docs/gradio/file. Running synchronous functions are not cancelled by `cancels`; revision-based output invalidation is therefore used.
- Project evidence: reports/heldout_test.json, reports/decision_policy.json, reports/split_summary.json and docs/MODEL_CARD.md.
