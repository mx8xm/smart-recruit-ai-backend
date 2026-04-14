param(
    [switch]$SkipModelCheck,
    [switch]$SkipDbCheck
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "[INFO] Smart Recruit AI Backend Launcher" -ForegroundColor Cyan
Write-Host "[INFO] Using local environment preference: .env.local" -ForegroundColor Cyan
Write-Host "[INFO] PostgreSQL stays external to the app package" -ForegroundColor Cyan
Write-Host "[INFO] If PostgreSQL is missing, use scripts\download_postgres_installer.ps1" -ForegroundColor Yellow

$RunArgs = @("-ExecutionPolicy", "Bypass", "-File", (Join-Path $ProjectRoot "scripts\run_local.ps1"))
if ($SkipModelCheck) {
    $RunArgs += "-SkipModelCheck"
}
if ($SkipDbCheck) {
    $RunArgs += "-SkipDbCheck"
}

& powershell @RunArgs
exit $LASTEXITCODE
