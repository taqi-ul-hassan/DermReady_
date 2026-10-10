# Technical handoff: steps 1–14

Required local-MVP work is complete through evaluation and technical delivery. The user excluded final presentation; no deck, final screenshots/video, portal submission, or public deployment was created.

## Completed

- Frozen held-out evaluation on 107 cases / 299 images: heldout_test.md.
- Paired blur and lighting sensitivity experiments with frozen policies: robustness.md.
- Explicit three-state denominators, coverage, intervals, confusion matrices and error review.
- Research-only model card, separate licenses/attribution, and reproduction instructions.
- 30 automated checks, all passed with private trained artifacts present.
- A genuinely new Linux CPU environment installed the full lock and passed imports, CPU execution, trained inference, Gradio construction, HTTP synthetic upload, and private-file blocking.
- Windows setup/launch helpers and novice-friendly ZIP-update instructions.
- Original synthetic capture targets for permitted public demos and a demo guide.
- Publication includes only selected source/docs, synthetic assets, and aggregate reports/plots. No patient image, raw case ID list, per-case prediction, model weight, upload, credential, or private split file is included.

## Scientific limits

The default single-image pipeline produced 12 suitable, 34 retake, and 61 uncertain outputs. Its weak case-label false-acceptance count was 1/23, and false-rejection count was 25/84. Models remain validation-selected and unchanged after final tests. Captured image proxies do not establish cause, framing, skin presence, diagnosis or clinical adequacy. See MODEL_CARD.md and evaluation reports for the small-sample limits.

## Final presentation handoff

The user must capture screenshots/record their working local app, prepare the final presentation, and submit through the official portal. The maintainer cloud browser could not reach the workspace's localhost server, so no UI screenshots are claimed. Use synthetic assets and aggregate plots for presentation; do not expose personal or dataset case records.

Published event deadline sources still disagree between EDT and AoE. The earlier schedule time is October 12, 2026 at 08:59 PKT; confirm the actual portal deadline yourself. Video is at most three minutes; FAQ write-up is at most 500 words. See docs/EVENT_RULES.md. No eligibility or challenge-theme fit is asserted.

Optional research enhancements, subgroup assurance, and external hosting are outside this local MVP. GitHub Actions checks are configured but remote execution has not been inspected.
