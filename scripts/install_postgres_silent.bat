@echo off
setlocal
color 0B
mode con:cols=100 lines=15
cls
set PROJECT_ROOT=%~dp0..
set INSTALLER=%PROJECT_ROOT%\data\postgresql-18.3-2-windows-x64.exe

if not exist "%INSTALLER%" (
    echo Installer not found:
    echo %INSTALLER%
    echo Run scripts\download_postgres_installer.py first.
    exit /b 1
)

echo.
echo.
echo.                                             SILENT MODE... shh!
echo.
echo This helper uses /S as requested for local testing.
echo Please verify installer flags locally before unattended use in other environments.
"%INSTALLER%" /S
exit /b %ERRORLEVEL%
