@echo off
setlocal
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
python scripts\download_postgres_installer.py %*
exit /b %ERRORLEVEL%
