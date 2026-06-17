@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

echo PharmaGuard AI local demo launcher
echo Starting via PowerShell...

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-pharmaguard-demo.ps1"
if errorlevel 1 (
  echo.
  echo Demo launcher failed. See the message above for details.
  pause
  exit /b 1
)

endlocal
