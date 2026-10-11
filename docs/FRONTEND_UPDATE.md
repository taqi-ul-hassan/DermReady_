# Install the reference frontend on Windows

This update contains the reference-style frontend, retake comparison, and the static evidence/example assets it needs. It does not contain or replace model files, your Python environment, or patient images.

1. Stop the running app: press Ctrl+C in its terminal.
2. Extract DermReady_Frontend_Update.zip into a temporary folder.
3. Copy ALL contents of that extracted folder into your existing project folder, the one containing app.py. Merge the src/, assets/ and reports/ folders and choose Replace for matching files. Do not create another nested DermReady folder.
4. Keep your existing checkpoints/ and .venv/ folders in place.
5. In PowerShell opened inside your project, run:

```powershell
.\.venv\Scripts\python.exe app.py
```

6. Open http://127.0.0.1:7860 and press Ctrl+F5 to refresh cached frontend assets.

No new application dependencies are introduced. The project expects the previously installed Gradio 6.30.0 environment. You can also double-click launch_windows.bat.

## Included design

Dark teal hero, mint headline, three workflow cards, research notice, current-mode banner, photograph-checking cards, retake comparison, and Evidence & limits tabs. Selected tabs use a mint underline. The layout stacks on small screens and preserves visible keyboard focus.

Without fitted artifacts the banner correctly says capture indicators only and the app returns uncertain. With your existing artifact files it uses the selected research model. Frontend changes do not change learned model parameters, thresholds or evaluation results.
