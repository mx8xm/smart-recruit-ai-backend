param(
    [switch]$Apply
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogsDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
$LogFile = Join-Path $ProjectRoot "cleanup_local.log"

$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$ArgsList = @("scripts/cleanup_local.py")
if ($Apply) {
    $ArgsList += "--apply"
}

Write-Host "Running local cleanup helper..." -ForegroundColor Cyan
Write-Host "Log file: $LogFile" -ForegroundColor DarkGray

& $PythonExe @ArgsList 2>&1 | Tee-Object -FilePath $LogFile
exit $LASTEXITCODE
