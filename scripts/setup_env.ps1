param(
    [string]$Python = "python",
    [string]$VenvName = "venv",
    [switch]$SkipUpgrade
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ArgsList = @("scripts/setup_env.py", "--python", $Python, "--venv-name", $VenvName)
if ($SkipUpgrade) {
    $ArgsList += "--skip-upgrade"
}

Write-Host "Preparing local Python environment..." -ForegroundColor Cyan
& $Python @ArgsList
exit $LASTEXITCODE
