@echo off
setlocal

set "ROOT=%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%ROOT%prepare_platform.py" %*
  exit /b %ERRORLEVEL%
)

python "%ROOT%prepare_platform.py" %*
exit /b %ERRORLEVEL%
