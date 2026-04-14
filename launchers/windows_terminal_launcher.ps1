param(
    [switch]$SkipModelCheck,
    [switch]$SkipDbCheck
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Launcher = Join-Path $ProjectRoot "scripts\launch_backend_terminal.ps1"

& powershell -ExecutionPolicy Bypass -File $Launcher @PSBoundParameters
exit $LASTEXITCODE
