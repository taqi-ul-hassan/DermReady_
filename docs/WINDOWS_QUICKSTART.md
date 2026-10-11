# Windows quick start

Your existing working installation does not need to be recreated. Double-click `launch_windows.bat` in the project folder to start it, then open http://127.0.0.1:7860. Keep its terminal open; Ctrl+C stops it. If the port is already in use, stop your earlier app terminal first.

## First installation

1. Install Python 3.12 and select Add Python to PATH.
2. Download the repository ZIP and extract it. Open the folder containing app.py.
3. Extract the supplied trained-artifact ZIP. Copy best.pt, quality_baseline.json and decision_policy.json directly into checkpoints/.
4. In File Explorer's address bar type `powershell` and press Enter.
5. Run these commands one at a time:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe app.py
```

Alternatively, setup_windows.ps1 runs the installation commands if your existing PowerShell policy permits scripts. No policy change or virtual-environment activation is required for the commands above.

## Updating a ZIP installation

Download/extract a fresh repository ZIP into a new folder. Copy your private checkpoints/ files from your previous installation. Create/install the new folder's environment using the commands above; do not copy or relocate .venv. You can keep using your old working app until ready. Git pull applies only to installations made with Git clone.

## Common issues

- Python version not found: install Python 3.12; `py -0p` lists installed interpreters.
- No matching package distribution: confirm 64-bit Python 3.12 and share the exact error.
- Features-only mode: confirm the three artifact files are directly in checkpoints/ with no extra nested folder.
- Connection refused: the terminal must still be running; wait for the local URL.
- Port in use: stop the earlier process or use `app.py --port 7861`, then open http://127.0.0.1:7861.

The maintainer's fresh trained-artifact checks are Linux/Python 3.12. The user reported a working Windows installation. Linux and Windows CPU CI passed for the comprehensive review, including dependencies, regression tests and live synthetic app APIs; private trained-artifact execution is not part of public CI. See reports/project_review_checks.json.


## Verify the installation

From the folder containing app.py, run:

```powershell
.\.venv\Scripts\python.exe scripts/check_installation.py --require-trained
```

The checker shows the active system, missing or nested artifact files, and whether the active model/policy match the published hashes. It does not download weights or read medical images. Without `--require-trained`, it also reports a capture-indicators-only installation. A fitted but different artifact may run; historical performance must not be attributed to it.
