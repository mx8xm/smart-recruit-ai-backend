@echo off
setlocal
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"
python scripts\setup_env.py %*
exit /b %ERRORLEVEL%
