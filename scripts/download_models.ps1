param(
    [switch]$CheckOnly
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$ArgsList = @("download_models.py")
if ($CheckOnly) {
    $ArgsList += "--check-only"
}

Write-Host "Checking/downloading AI models..." -ForegroundColor Cyan
& $PythonExe @ArgsList
exit $LASTEXITCODE
