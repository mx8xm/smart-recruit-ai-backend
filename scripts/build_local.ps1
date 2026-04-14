param(
    [ValidateSet("onedir", "onefile", "both")]
    [string]$Mode = "both",
    [switch]$PredownloadModels
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "venv\\Scripts\\python.exe was not found. Run scripts\\setup_env.ps1 first." -ForegroundColor Red
    exit 1
}

$OutputRoot = Join-Path $ProjectRoot "output"
$DistPath = Join-Path $OutputRoot "dist"
$BuildPath = Join-Path $OutputRoot "build"
$ArtifactsPath = Join-Path $OutputRoot "artifacts"
New-Item -ItemType Directory -Force -Path $DistPath, $BuildPath, $ArtifactsPath | Out-Null

if ($PredownloadModels) {
    Write-Host "[INFO] Pre-downloading models before packaging..." -ForegroundColor Cyan
    & $PythonExe download_models.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Invoke-Build([string]$BuildMode) {
    Write-Host "[INFO] Building $BuildMode package..." -ForegroundColor Cyan
    $env:PYI_BUILD_MODE = $BuildMode
    & $PythonExe -m PyInstaller --noconfirm --clean packaging\backend.spec --distpath $DistPath --workpath $BuildPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Mode -eq "onedir" -or $Mode -eq "both") {
    Invoke-Build "onedir"
    Compress-Archive -Path "$DistPath\smart-recruit-backend\*" -DestinationPath "$ArtifactsPath\smart-recruit-backend-onedir.zip" -Force
}

if ($Mode -eq "onefile" -or $Mode -eq "both") {
    Invoke-Build "onefile"
    Copy-Item "$DistPath\smart-recruit-backend.exe" "$ArtifactsPath\smart-recruit-backend-onefile.exe" -Force
    Compress-Archive -Path "$DistPath\smart-recruit-backend.exe" -DestinationPath "$ArtifactsPath\smart-recruit-backend-onefile.zip" -Force
}

Write-Host "[OK] Local build artifacts are in output\\artifacts" -ForegroundColor Green
