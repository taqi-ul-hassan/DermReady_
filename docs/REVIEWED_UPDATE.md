# Install the reviewed update on Windows

1. Stop DermReady with Ctrl+C in its PowerShell terminal.
2. Extract DermReady_Reviewed_Update.zip.
3. Copy ALL extracted contents into your existing project folder (the one containing app.py, .venv and checkpoints).
4. Merge src/, assets/, reports/ and docs/ folders. Choose Replace the files in the destination for matching files. Do not copy the extracted parent folder as another nested project.
5. Keep .venv/ and checkpoints/ untouched; neither is present in this update.
6. Run from PowerShell in the project:

```powershell
.\.venv\Scripts\python.exe app.py
```

7. Open http://127.0.0.1:7860 and press Ctrl+F5.

The update changes app.py and the source modules listed in the ZIP. It includes the synthetic example/evidence assets required by the UI. No model weights, decision-policy artifact, training data or new dependency requirements are included.

## Check after updating

- The yellow research notice no longer appears below the hero. Research limits remain in Evidence & limits.
- Run a photo check. Suggested next action starts with Why this result and explains uncertainty or the decision band.
- Choose another photograph. The previous preview, assessment and table clear; click Check photograph for the new upload.
- Clear the file: the app asks for a photograph and does not keep the previous result.
- Compare two captures, then change either input: the old pair/table clear before a fresh comparison.
- Body/table text is larger, and the evidence-chart title sits above the chart.

## Accuracy and bias

These are software correctness and explanation fixes. They do not train a better model or change the frozen policy. The existing baseline returned uncertain for 61/107 held-out cases. Demographic fairness and clinical accuracy for every dermatology image are not established. Read TECHNICAL_BIAS_AUDIT.md for the audit and the independent validation needed before claiming broader performance.
