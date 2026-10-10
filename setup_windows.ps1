$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 and rerun this script.' }
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { throw 'CPU PyTorch installation failed.' }
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed.' }
Write-Host 'Setup complete. Run launch_windows.bat to open DermReady.'
