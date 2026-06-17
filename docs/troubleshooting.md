# Troubleshooting

## PowerShell Blocks npm.ps1

Use `npm.cmd` instead:

```powershell
cd frontend
npm.cmd run dev
```

The Windows launch scripts already prefer `npm.cmd`.

## Port 3000 Is Already In Use

The frontend uses port `3000` by default.

Options:

- Stop the existing service with `stop-pharmaguard-demo.bat`.
- Close the terminal running the old frontend.
- Manually launch on another port:

```powershell
cd frontend
npm.cmd run dev -- --port 3001
```

## Backend Port 8000 Is Already In Use

The backend uses port `8000` by default.

Options:

- Stop the existing service with `stop-pharmaguard-demo.bat`.
- Close the terminal running the old backend.
- Check the running backend at `http://localhost:8000/health`.

## Python Not Found

Install Python 3.11+ or create a project virtual environment. The launcher prefers:

- `backend/.venv/Scripts/python.exe`
- `.venv/Scripts/python.exe`
- system `python`

Manual setup:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Node Or npm Not Found

Install Node.js with npm. Then install frontend dependencies:

```powershell
cd frontend
npm.cmd install
```

## Dependencies Missing

Backend:

```powershell
cd backend
pip install -r requirements.txt
```

Frontend:

```powershell
cd frontend
npm.cmd install
```

## Tesseract Missing

This is okay for the local demo. Tesseract is optional, disabled by default, and policy-gated. The default OCR demo uses local mock/synthetic providers.

## Browser Does Not Open Automatically

Open the page manually:

```text
http://localhost:3000
```

Evidence page:

```text
http://localhost:3000/evaluation
```

## How To Stop Stuck Processes

Run:

```powershell
.\stop-pharmaguard-demo.ps1
```

Or close the backend/frontend terminal windows.

If needed, inspect listeners:

```powershell
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8000"
```

Then stop a process by PID:

```powershell
Stop-Process -Id <PID> -Force
```

Only stop processes you recognize as part of your local demo.
