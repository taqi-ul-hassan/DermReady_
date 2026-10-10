# Project scope and decisions

## Goal
Build a research-only suitability gate for dermatology photography, with measurable quality indicators and conservative retake guidance.

## Decisions established during scaffolding
- Solo 48-hour MVP based on the attached project proposal.
- SCIN is the intended data source; access, schema, and license remain to be reviewed.
- Case-level labels, splits, and planned image-embedding aggregation.
- Single-image upload for the MVP; evaluate and document mismatch with multi-image supervision.
- Three states: likely suitable for review, may need a retake, uncertain.
- Separate learned gradability from capture-quality proxies.
- Validation-selected thresholds; untouched test set for final reporting.
- No disease diagnosis or claims of clinical adequacy.
- No dataset, weights, credentials, or private uploads in Git.
- MIT license for original project code only.

## Open decisions
- Confirm label fields, missing-value encoding, and consensus feasibility.
- Confirm class order and score mapping after audit.
- Verify aggregation and single-image evaluation protocol.
- Choose validation thresholds and report uncertainty coverage.
- Local dependency versions verified and pinned; live Colab verification and hosting upload/cache checks remain pending.
- Confirm the current event rules, deadline, permitted hosting, public-repository requirements, and hacking window. These have not been verified.

## Delivery gates
At hour 2: pivot to permitted UI demonstration data if access/label interpretation is blocked.
At hour 12: deliver an honestly labeled quality-feature baseline if the classifier is incomplete.
Freeze features before recording and submission.
