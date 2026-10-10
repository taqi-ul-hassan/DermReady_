# Steps 6–10 completion report

## Step 6: image validation and preprocessing

All 1,674 train/validation image references were downloaded, checked against available object MD5, and decoded successfully. No test images were downloaded or decoded during step 6. The earlier pre-split data audit decoded six images later assigned to test, solely to verify readability; they were not used for training, feature/threshold selection, or model evaluation. Validated PNG/JPEG/still-WebP input handling, corrupt/tiny/animated input rejection, EXIF orientation, grayscale/alpha handling, and bounded file/pixel/aspect limits.

The original oriented RGB photograph is used for capture measurements. The model receives a 224×224 aspect-preserving letterbox and ImageNet normalization. Only training uses horizontal flips; blur/exposure/compression augmentation is excluded because it can change the quality task. Inference and validation use the same deterministic transform.

## Step 7: quality-feature baseline

Extracted focus, brightness, contrast, clipping, resolution, and aspect-ratio proxies. Case-level mean/min/max features and image count were used for a scaled, class-balanced logistic regression fitted on TRAIN only. No demographic or disease-category fields were used. Distribution thresholds use validation capture features and are not defect ground truth.

## Step 8: pretrained image baseline

Loaded timm mobilenetv3_small_100.lamb_in1k ImageNet weights, added a two-output case head, and aggregated image embeddings by mean. Completed three epochs on CPU: one head-only warmup, then two full-backbone fine-tuning epochs. Batch size 8 cases; learning rates 0.001 for warmup and 0.0001 for fine-tuning. Class-balanced cross entropy, fixed seed 42, stable pretrained batch-normalization statistics.

Later fine-tuning degraded validation performance. The selected checkpoint is therefore epoch 1: pretrained encoder plus trained case head. It is not a randomly initialized or fully fine-tuned selected backbone. This limitation is retained rather than hidden.

| Validation measure at threshold 0.5 | Quality baseline | Selected MobileNet |
| --- | ---: | ---: |
| Case-level balanced accuracy | 0.674 | 0.656 |
| Case-level ROC-AUC | 0.729 | 0.738 |
| Single-image weak-label ROC-AUC | 0.606 | 0.612 |

These are validation-selection measurements, not final test results. The single-image figures reveal weak discrimination and a real mismatch with multi-image case supervision.

## Step 9: three-state policy

Validation uses one fixed first-listed photograph per case with the case label as a weak proxy. Scores are uncalibrated. Two score thresholds are selected under documented empirical constraints; quality flags block acceptance, and unsupported modes, near-constant images, or high-frequency signals outside the reference range become uncertain. This does not establish a general unrelated-image detector or clinically safe threshold.

Both models have policies. The default feature baseline was chosen by fewer validation false acceptances after full guards, then correctly accepted gradable cases, then ROC-AUC. MobileNet remains available with --model cnn.

| Full guarded validation pipeline | Quality baseline (default) | MobileNet |
| --- | ---: | ---: |
| Likely suitable | 13 | 16 |
| May need retake | 34 | 38 |
| Uncertain | 59 | 52 |
| False acceptance / 23 ungradable cases | 0 | 2 |
| False rejection / 83 gradable cases | 22 | 27 |

For the default's 0/23 false acceptances, the descriptive Wilson 95% interval is 0–14.3%. Threshold/model selection on the same validation set introduces optimism that this interval does not account for. Zero observed events do not establish zero risk. The full policy and denominators are in decision_policy.json; the single-view task remains weakly supervised.

## Step 10: integrated Gradio demo

The app uploads one image, previews it, displays the three-state result, exposes interpretable indicators, and gives supported non-diagnostic guidance and framing caveats. Inference is independent of UI and loads artifacts once. CPU checkpoint loading and baseline JSON inference both passed. Missing trained artifacts are explicitly features-only; the app does not use random weights as a trained model.

The synthetic-noise API smoke test exposed an acceptance weakness; an out-of-range texture guard was added and the final synthetic upload returns uncertain. Local HTTP upload/API execution passed, and serving a private dataset file returned HTTP 403. No public share URL or deployment was created. Gradio temporary files are configured for periodic cleanup; no claim of instant deletion is made.

Final checks: 26 tests passed, live local API smoke passed, dependencies consistent, training and inference CPU paths verified. The held-out test split remains untouched for step 11.

## Remaining work

Step 11: frozen held-out evaluation, uncertainty intervals, error analysis. Step 12: controlled held-out perturbation experiments. Later steps: optional inspection/subgroups, final documentation/reproduction on a clean machine, demo video, and submission. Event sources disagree about AoE versus EDT deadline; see docs/EVENT_RULES.md.
