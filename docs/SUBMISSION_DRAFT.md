# Submission text draft

## DermReady: check your capture, improve it, compare again

DermReady helps people preparing photographs for remote dermatology review notice potentially correctable capture problems. It is a research prototype, not a diagnosis or guarantee of clinical adequacy.

Users upload a photograph, inspect focus, exposure, contrast and resolution indicators, and receive a prioritized next action. They can upload a newly captured photograph to compare measurable changes side by side. No automatic enhancement changes the original image. A visible uncertainty state explains when the prototype cannot support an acceptance decision.

We audited Google's SCIN dataset, documented reviewer-label semantics, and retained 710 cases under an explicit consensus policy. Related cases sharing image paths or known content hashes stay in the same split. We trained a quality-feature logistic-regression baseline and a MobileNetV3-Small case model. Validation selected the feature baseline as default; models and policies were frozen before final testing.

On 107 held-out cases, the default single-image workflow produced 12 suitable, 34 retake and 61 uncertain outputs. Against weak case-label proxies, false acceptance was 1/23 and false rejection was 25/84. Decision coverage was 43%. The false-acceptance 95% interval was 0.8–21.0%, so these findings do not demonstrate clinical safety. Controlled blur and lighting experiments show indicator/policy sensitivity, not clinical accuracy.

The key limitation is supervision: SCIN labels describe whole cases, while the app accepts one photograph. Retaking cannot necessarily resolve insufficient clinical information. Single-image expert labels, independent external evaluation and adequately powered subgroup analysis are future work.

Code, aggregate evidence, synthetic examples and reproduction instructions are public. Patient data and trained weights remain outside Git. The app runs locally with temporary-file cleanup; externally hosted retention has not been validated. Without fitted artifacts, the app transparently provides indicators and comparison only.

Built with Python, Gradio, OpenCV, scikit-learn, PyTorch and timm. SCIN and pretrained-model attribution appear in the repository. ChatGPT/Codex assisted implementation and documentation.

## Submission checklist (not part of the write-up)

- Record the actual working app; show the active mode honestly.
- Supply a permitted reviewer route to fitted artifacts or a recorded trained demonstration. Do not publish patient data or private case records.
- Verify the official theme, eligibility, deadline and portal requirements.
- Include repository URL and video; confirm required word/time limits.
- This draft does not constitute portal submission or a recorded demo.
