@echo off
setlocal
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
python scripts\run_local.py %*
exit /b %ERRORLEVEL%
