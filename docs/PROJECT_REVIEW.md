# Comprehensive project review

Reviewed 11 October 2026. Scope: repository structure, SCIN audit/label policy, grouped splitting, preprocessing, baseline/CNN training, validation policy, final evaluation, robustness testing, Colab notebooks, Windows setup, Gradio app, privacy controls, tests and documentation. No final presentation or submission was created.

## Overall assessment

DermReady has a functioning research pipeline and a useful local capture-review workflow. Its strongest distinction is transparent evidence: it separates capture measurements from learned gradability, explains uncertainty, supports side-by-side retake comparison, and preserves frozen evaluation artifacts. It should be presented as a research capture assistant. Current evidence does not support reliable suitability decisions for all dermatology images.

The main performance limitation is supervision and distribution coverage, rather than an obvious threshold bug. Only 710 of 5,033 SCIN cases meet the selected consensus policy. Labels describe whole cases, whereas the app receives one image. The selected baseline returned uncertain on 61/107 held-out first images (57.0%). Lowering thresholds to make the app look more decisive would change the tested policy without establishing better accuracy.

## Findings and implemented improvements

| Area | Finding | Action and practical effect |
| --- | --- | --- |
| Evaluation integrity | Final evaluation hashed split CSVs but loaded cases.jsonl separately without verifying their agreement. Robustness did not recheck the split cohort. | Added private provenance verification of prepared/source artifacts, case membership/labels/groups/image counts and leakage before image access. New final freezes include manifest hashes; robustness verifies the corresponding cohort. |
| Artifact provenance | A valid but different checkpoint/policy could run while the UI displayed published historical results. | Added SHA-256 identity checks in Evidence & limits. The UI explicitly distinguishes matching published artifacts, unmatched artifacts and indicator-only sessions. Identity is not a new accuracy evaluation. |
| Setup troubleshooting | Users could accidentally extract artifacts into an extra folder or run without fitted files. | Added scripts/check_installation.py: active mode, trained readiness, per-file identity and nested-folder guidance. It reads no medical images and performs no downloads. |
| Artifact validation | Some malformed model containers or numeric strings could pass partial validation and fail later. | Require expected object structures and numeric bands/arrays. Invalid inputs fall back to explicitly labeled indicators instead of producing suitability scores. |
| Metrics | Binary metrics lacked checks for invalid, mismatched, nonfinite or out-of-range inputs; integer conversion could hide fractional labels. | Added validation before metric computation. Three-state metrics now also reject fractional labels. Frozen valid inputs retain the same calculations. |
| Capture interpretation | Raw numeric values were hard to interpret and could look like clinical quality grades. | Added an interpretation column: inspect visually, no reference flag, or no validated threshold/reference. The app explains that an untriggered proxy is not a quality guarantee. |
| Retake comparison | Identical uploads or substantial geometry/resolution changes could be read as a meaningful retake comparison. | Added identical-decoded-pixel, aspect/orientation, pixel-count and color-conversion notices. Comparison remains descriptive and makes no clinical improvement claim. |
| User workflow | A next action existed, but capture preparation was unstructured. | Added an optional preparation checklist and progress display. These are user checks, never model inputs or a suitability score. |
| Startup paths | Launching app.py from another working directory could miss the default artifacts/reports and block the wrong private data folder. | Default artifact/report paths and private-path blocking now resolve from the application directory. Explicit checkpoint paths remain supported. |
| Image cache | Distinct object paths with the same basename could collide in the flat cache. | Reject cache filename collisions before downloading; existing SCIN behavior is preserved. |
| HTTP privacy test | Testing a nonexistent private path could yield weaker evidence than testing an actual file. | Smoke test now creates and cleans up a real temporary synthetic marker inside the blocked data directory. |
| Test discovery | Generic pytest discovery could import evaluation scripts as tests. | Added pytest.ini to scope discovery to tests/. |
| Windows coverage | The user uses Windows, but CI was configured only for Linux. | Added Linux/Windows CPU CI matrix and installation-check execution. Both Linux and Windows jobs passed; the verified run is linked in project_review_checks.json. Public CI uses synthetic inputs and has no private trained artifacts. |
| Documentation | Privacy/reports pages still said implementation/evaluation were pending; test counts and screenshot wording were stale. | Updated operational documentation, report index and test guide. README links this review and labels the earlier screenshot revision. |

## Scientific and bias review

The label parser explicitly handles the two unambiguous categories, excludes ambiguous/no-discernible-pathology votes and ties, and stops on unknown tokens. Connected-component grouping includes excluded bridge cases, shared paths and available object MD5 hashes. Model fitting uses training cases; model/threshold selection uses validation. Test outcomes did not select the default or thresholds. The default remains the quality-feature baseline; the warmup CNN checkpoint remains available because later fine-tuning performed worse on validation.

These are useful safeguards, with material limits:

- **Selected cohort:** strict reviewer consensus retains 14.1% of source cases. Reported performance does not describe all SCIN contributors or all conditions.
- **Weak single-image labels:** case-level gradability is not a definitive suitability label for each constituent image. Retaking may not repair missing clinical information.
- **Small negative cohort:** the default has 1/23 weak-proxy false acceptances; its published 95% interval is approximately 0.8–21.0%. This does not establish a low clinical error rate. False rejection is 25/84 and uncertainty is 61/107.
- **Brightness and texture proxies:** skin appearance, background, lighting and device processing can affect measurements. Brightness is not skin tone, and higher focus/contrast values are not automatically better.
- **Fairness remains unmeasured:** there is no adequately powered subgroup evaluation by skin tone, age, condition or device for the retained cohort. Similar uncertainty rates across the two outcome classes are not demographic fairness evidence.
- **Unsupported scope:** no validated skin detector, anatomical framing assessment or unrelated-image detector is present. Dermoscopic, histology, pediatric and outside-source inputs have no separate validation.
- **Duplicate coverage:** exact path/known-byte grouping does not detect perceptual near duplicates or undocumented contributor overlap.

No thresholds, trained weights, preferred model or published accuracy metrics were changed in this review. Capture workflow improvements should not be described as accuracy gains. See TECHNICAL_BIAS_AUDIT.md and MODEL_CARD.md for the earlier detailed scientific review.

## Verification and boundaries

The review uses the current source and public aggregate reports. Private weights, original dataset, split manifests and per-case prediction files are absent from this workspace. Automated integrity tests use synthetic manifests and altered-input scenarios; app checks use artificial capture targets. The private trained round-trip remains skipped here. No new patient evaluation, retraining, demographic audit, clinical validation, external deployment or browser screenshot comparison was performed.

Current executable results and the successful Linux/Windows CI run are recorded in reports/project_review_checks.json. Existing scientific reports remain historical evidence for the exact published artifacts. Source changes do not retroactively validate new inputs or installations.

## Research priorities that would materially improve the project

| Priority | Work needed | Evidence required before claiming improvement |
| --- | --- | --- |
| 1 | Obtain independent expert image-level suitability annotations, including relevant view/context requirements. | Predefined task, annotation protocol, agreement analysis and an untouched evaluation cohort. |
| 2 | Evaluate uncertainty and errors across skin tone, age, condition and device, with missingness reporting. | Consent/terms-compatible metadata, sufficiently sized groups, counts and uncertainty intervals. Do not infer protected attributes from brightness. |
| 3 | Compare single-image and multi-image workflows. | Validation-selected aggregation/policies and a new held-out cohort; existing test cases must not be used for tuning. |
| 4 | Test across independent capture sources and real camera changes. | External evaluation and separately labeled retake pairs; synthetic blur/exposure sensitivity is insufficient. |
| 5 | Investigate calibrated scores and a validated out-of-scope input gate. | Dedicated validation and independent test evidence. Avoid presenting uncalibrated scores as probabilities. |

For a demonstration, emphasize the measurable workflow, understandable uncertainty and traceable evidence. These are implemented strengths. Broader clinical accuracy and fairness require the research above.
