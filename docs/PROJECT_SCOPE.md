# Project scope and decisions

## Goal
Build a research-only suitability gate for dermatology photography, with measurable quality indicators and conservative retake guidance.

## Decisions established during scaffolding
- Solo 48-hour MVP based on the attached project proposal.
- SCIN official CSV access, current schema/license review, and sampled image loading are complete; see reports/data_audit.md.
- Case-level labels, splits, and planned image-embedding aggregation.
- Single-image upload for the MVP; evaluate and document mismatch with multi-image supervision.
- Three states: likely suitable for review, may need a retake, uncertain.
- Separate learned gradability from capture-quality proxies.
- Validation-selected thresholds; untouched test set for final reporting.
- No disease diagnosis or claims of clinical adequacy.
- No dataset, weights, credentials, or private uploads in Git.
- MIT license for original project code only.

## Open decisions
- Confirmed categorical gradability mapping and strict consensus: 710 eligible cases before missing-image handling. No-discernible-pathology votes remain outside the binary task. Connected-case grouping for shared paths/content hashes and saved leakage-free splits are implemented.
- Use label 0 for operational ungradable and 1 for operational gradable; preserve raw vote provenance. Validate model output mapping during implementation.
- Case-level mean embedding aggregation implemented; single-image validation uses first-listed image with a weak case-label proxy. Frozen held-out testing is complete; see reports/heldout_test.md.
- Validation thresholds and uncertainty coverage recorded in reports/decision_policy.json; the default quality baseline has 59/106 uncertain validation outputs.
- Local dependency versions verified and pinned; live Colab verification and hosting upload/cache checks remain pending.
- Event rules reviewed; deadline sources conflict (AoE versus EDT), documented in docs/EVENT_RULES.md. User eligibility/theme still unverified. No public hosting was performed.

## Delivery gates
At hour 2: pivot to permitted UI demonstration data if access/label interpretation is blocked.
At hour 12: deliver an honestly labeled quality-feature baseline if the classifier is incomplete.
Freeze features before recording and submission.
