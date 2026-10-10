@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Python environment is missing. Follow docs\WINDOWS_QUICKSTART.md first.
  pause
  exit /b 1
)
echo DermReady: open http://127.0.0.1:7860 when the server is ready.
echo Keep this window open. Press Ctrl+C to stop.
".venv\Scripts\python.exe" app.py
if errorlevel 1 pause
