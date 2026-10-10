# Local demo preparation

No final slide deck, presentation video, or submission is included. The application and the following materials are ready for your own final presentation.

1. Start with launch_windows.bat or your existing Python command. Open http://127.0.0.1:7860.
2. Point out the research-only notice and three possible states.
3. Upload assets/demo/synthetic_original.png and click Check photograph. This is an artificial capture target, not a skin photograph; its state does not demonstrate clinical accuracy.
4. Clear the input and upload synthetic_blur.png, then synthetic_dark.png. Compare focus/exposure indicators and qualified guidance.
5. Upload synthetic_noise.png. It should return uncertain under the frozen policy's out-of-reference texture guard. This guard is not a general unrelated-image detector.
6. For scientific results, show reports/heldout_test.md and reports/robustness.md. State that single-image labels are weak case-derived proxies, 61/107 baseline outputs were uncertain, and clinical adequacy is not established.

## Before your final recording

Close private browser tabs and notifications. Use the synthetic targets, not your personal medical photographs or SCIN case records. Keep the app local. Show the report rather than searching for a patient image that yields a desired state. All three state boundaries are checked in automated tests; there is no scripted replacement of live results.

## Backup

Keep the trained-artifact ZIP and your working project folder available offline. The trained app requires no runtime weight download. Aggregate plots and reports are in reports/. Screenshot capture was unavailable in the maintainer environment because its browser could not reach the local workspace app. Capture screenshots from your working local app as part of your final presentation. If the app fails during presentation, use the documented evaluation and your own captured screenshots honestly as backup. Creating the final presentation/recording and submitting it are left to the user.
