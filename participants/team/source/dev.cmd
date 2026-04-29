@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "BACKEND_PORT=5000"
set "FRONTEND_PORT=5173"
set "PYTHON_EXE="

for %%P in ("%ROOT%.venv\Scripts\python.exe" "%BACKEND_DIR%\.venv\Scripts\python.exe") do (
  if not defined PYTHON_EXE if exist "%%~P" (
    "%%~P" -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=%%~P"
  )
)

if not defined PYTHON_EXE (
  echo Windows Python virtualenv not found or invalid.
  echo Checked:
  echo   "%ROOT%.venv\Scripts\python.exe"
  echo   "%BACKEND_DIR%\.venv\Scripts\python.exe"
  echo.
  for %%V in ("%ROOT%.venv\pyvenv.cfg" "%BACKEND_DIR%\.venv\pyvenv.cfg") do (
    if exist "%%~V" (
      findstr /b /c:"home = /" "%%~V" >nul 2>nul
      if not errorlevel 1 echo Detected Linux virtualenv at "%%~dpV"; it is ignored on Windows.
    )
  )
  echo Create or recreate a Windows virtualenv:
  echo   prepare.cmd --force-venv
  exit /b 1
)

if not exist "%BACKEND_DIR%" (
  echo Backend folder not found: "%BACKEND_DIR%"
  exit /b 1
)

if not exist "%FRONTEND_DIR%" (
  echo Frontend folder not found: "%FRONTEND_DIR%"
  exit /b 1
)

call :ensure_port_available "%BACKEND_PORT%" "backend"
if errorlevel 1 exit /b 1

call :ensure_port_available "%FRONTEND_PORT%" "frontend"
if errorlevel 1 exit /b 1

echo Using Python: "%PYTHON_EXE%"
echo Applying database migrations...
pushd "%BACKEND_DIR%"
"%PYTHON_EXE%" -m flask --app wsgi db upgrade
if errorlevel 1 (
  popd
  exit /b 1
)
popd

start "backend" /D "%BACKEND_DIR%" "%PYTHON_EXE%" -m flask --app wsgi run --debug --port "%BACKEND_PORT%"
start "frontend" /D "%FRONTEND_DIR%" cmd /k npm run dev

echo Backend and frontend started in separate cmd windows.
exit /b 0

:ensure_port_available
set "PORT_TO_CHECK=%~1"
set "SERVICE_NAME=%~2"
set "PORT_PID="
for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /R /C:":%PORT_TO_CHECK% .*LISTENING"') do (
  if not defined PORT_PID set "PORT_PID=%%P"
)

if defined PORT_PID (
  echo Port %PORT_TO_CHECK% for %SERVICE_NAME% is already in use by PID %PORT_PID%.
  echo Stop that process and run dev.cmd again.
  exit /b 1
)

exit /b 0
