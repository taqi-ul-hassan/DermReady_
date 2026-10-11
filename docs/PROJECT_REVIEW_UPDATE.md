# Apply the comprehensive review update on Windows

1. Stop the running app with Ctrl+C in its terminal.
2. Extract DermReady_Project_Review_Update.zip into a temporary folder.
3. Copy its contents into your existing DermReady project folder, where app.py is located. Merge folders and replace matching files. Keep your existing .venv and private checkpoints files. Do not copy the ZIP's parent folder as an extra nested project folder.
4. Open PowerShell in that project folder and run:

```powershell
.\.venv\Scripts\python.exe scripts/check_installation.py --require-trained
.\.venv\Scripts\python.exe app.py
```

The installation checker reports the active system and artifact identity. If it reports capture indicators only, fix missing/nested artifact files before expecting learned suitability output. No new dependencies or retraining are required for an existing working installation.

Open http://127.0.0.1:7860 and refresh with Ctrl+F5. The review table now interprets indicators. Compare a retake includes an optional preparation checklist and comparability notices. Evidence & limits identifies whether the installed model/policy match the historical evaluated artifacts. The removed notice below the header stays removed.

Read PROJECT_REVIEW.md for the full findings and remaining research gaps. Frozen model weights, score thresholds and published scientific results are unchanged. The update ZIP contains no trained artifacts or patient data.
