param(
    [switch]$SkipModelCheck,
    [switch]$SkipDbCheck
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogsDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
$LogFile = Join-Path $LogsDir "run_local.log"

Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$ArgsList = @("scripts/run_local.py")
if ($SkipModelCheck) {
    $ArgsList += "--skip-model-check"
}
if ($SkipDbCheck) {
    $ArgsList += "--skip-db-check"
}

Write-Host "Starting Smart Recruit AI local runner..." -ForegroundColor Cyan
& $PythonExe @ArgsList 2>&1 | Tee-Object -FilePath $LogFile
exit $LASTEXITCODE
