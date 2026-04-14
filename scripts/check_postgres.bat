@echo off
setlocal
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
python scripts\check_postgres.py %*
exit /b %ERRORLEVEL%
