param(
    [switch]$EnsureTables
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$ArgsList = @("scripts/check_postgres.py")
if ($EnsureTables) {
    $ArgsList += "--ensure-tables"
}

Write-Host "Running PostgreSQL preflight..." -ForegroundColor Cyan
& $PythonExe @ArgsList
exit $LASTEXITCODE
