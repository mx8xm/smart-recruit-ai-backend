param(
    [switch]$SkipModelCheck,
    [switch]$SkipDbCheck
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RunnerScript = Join-Path $ProjectRoot "scripts\start_backend.ps1"

$Arguments = @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $RunnerScript)
if ($SkipModelCheck) {
    $Arguments += "-SkipModelCheck"
}
if ($SkipDbCheck) {
    $Arguments += "-SkipDbCheck"
}

$WindowsTerminal = Get-Command wt.exe -ErrorAction SilentlyContinue
if ($WindowsTerminal) {
    Write-Host "Launching backend inside Windows Terminal..." -ForegroundColor Cyan
    & $WindowsTerminal.Source new-tab --startingDirectory $ProjectRoot powershell @Arguments
    exit $LASTEXITCODE
}

$PowerShell = Get-Command powershell.exe -ErrorAction SilentlyContinue
if ($PowerShell) {
    Write-Host "Windows Terminal not found. Falling back to PowerShell." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList $Arguments -WorkingDirectory $ProjectRoot
    exit $LASTEXITCODE
}

Write-Host "PowerShell not found. Falling back to cmd.exe." -ForegroundColor Yellow
$CmdArgs = @("/k", "powershell -ExecutionPolicy Bypass -File `"$RunnerScript`"")
Start-Process cmd.exe -ArgumentList $CmdArgs -WorkingDirectory $ProjectRoot
