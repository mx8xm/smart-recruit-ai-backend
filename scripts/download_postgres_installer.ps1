param()

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "Downloading PostgreSQL installer to .\data ..." -ForegroundColor Cyan
& $PythonExe scripts\download_postgres_installer.py
exit $LASTEXITCODE
