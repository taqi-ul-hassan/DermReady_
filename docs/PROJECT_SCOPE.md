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
- Verify aggregation and single-image evaluation protocol.
- Choose validation thresholds and report uncertainty coverage.
- Local dependency versions verified and pinned; live Colab verification and hosting upload/cache checks remain pending.
- Confirm the current event rules, deadline, permitted hosting, public-repository requirements, and hacking window. These have not been verified.

## Delivery gates
At hour 2: pivot to permitted UI demonstration data if access/label interpretation is blocked.
At hour 12: deliver an honestly labeled quality-feature baseline if the classifier is incomplete.
Freeze features before recording and submission.
