@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

echo PharmaGuard AI local demo stopper
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%stop-pharmaguard-demo.ps1"
if errorlevel 1 (
  echo.
  echo Demo stop script failed. See the message above for details.
  pause
  exit /b 1
)

endlocal
