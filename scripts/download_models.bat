@echo off
setlocal
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
python download_models.py %*
exit /b %ERRORLEVEL%
