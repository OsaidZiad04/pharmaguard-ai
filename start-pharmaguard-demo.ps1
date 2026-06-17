$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"
$BackendVenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
$RootVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Write-Status($Message) {
    Write-Host "[PharmaGuard AI] $Message"
}

function Resolve-Python {
    if (Test-Path $BackendVenvPython) {
        Write-Status "Using backend virtual environment: $BackendVenvPython"
        return $BackendVenvPython
    }

    if (Test-Path $RootVenvPython) {
        Write-Status "Using root virtual environment: $RootVenvPython"
        return $RootVenvPython
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        Write-Status "No project virtual environment found. Using system Python."
        return $pythonCommand.Source
    }

    throw "Python was not found. Install Python 3.11+ or create backend\.venv, then rerun this launcher."
}

function Resolve-Npm {
    $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($npmCommand) {
        return $npmCommand.Source
    }

    $npmFallback = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmFallback) {
        return $npmFallback.Source
    }

    throw "npm was not found. Install Node.js/npm, then rerun this launcher."
}

if (!(Test-Path $BackendDir)) {
    throw "Missing backend directory: $BackendDir"
}

if (!(Test-Path $FrontendDir)) {
    throw "Missing frontend directory: $FrontendDir"
}

$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (!$nodeCommand) {
    throw "Node.js was not found. Install Node.js 20+ or a compatible version, then rerun this launcher."
}

$PythonExe = Resolve-Python
$NpmExe = Resolve-Npm

if (!(Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Status "Warning: frontend\node_modules was not found. Run 'cd frontend && npm.cmd install' if the frontend window fails."
}

Write-Status "Tesseract is optional and remains disabled by default."
Write-Status "Starting backend at http://localhost:8000"
Write-Status "Starting frontend at http://localhost:3000"

$BackendCommand = @"
`$ErrorActionPreference = 'Stop'
Set-Location '$BackendDir'
Write-Host 'PharmaGuard AI Backend'
Write-Host 'URL: http://localhost:8000'
Write-Host 'Safety: prototype only; pharmacist review required.'
& '$PythonExe' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"@

$FrontendCommand = @"
`$ErrorActionPreference = 'Stop'
Set-Location '$FrontendDir'
Write-Host 'PharmaGuard AI Frontend'
Write-Host 'URL: http://localhost:3000'
Write-Host 'Use npm.cmd on Windows to avoid npm.ps1 execution policy issues.'
& '$NpmExe' run dev -- --hostname 127.0.0.1 --port 3000
"@

Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $BackendCommand) -WorkingDirectory $BackendDir
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $FrontendCommand) -WorkingDirectory $FrontendDir

Write-Status "Opening browser shortly. If it opens before the frontend is ready, refresh after a few seconds."
Start-Sleep -Seconds 6
Start-Process "http://localhost:3000"

Write-Host ""
Write-Status "Demo launch requested."
Write-Status "Main dashboard: http://localhost:3000"
Write-Status "Evidence page: http://localhost:3000/evaluation"
Write-Status "Backend health: http://localhost:8000/health"
Write-Status "To stop services, run stop-pharmaguard-demo.bat or stop-pharmaguard-demo.ps1."
