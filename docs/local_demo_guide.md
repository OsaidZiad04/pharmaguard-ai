# Local Demo Guide

This guide helps reviewers run PharmaGuard AI locally with minimal terminal work.

PharmaGuard AI is a pharmacist-centered prototype. It is not clinically validated, not a medical device, and not a patient-facing advisor. Use synthetic data only.

## One-Click Windows Launch

From the repository root, double-click:

```text
start-pharmaguard-demo.bat
```

Or run:

```powershell
.\start-pharmaguard-demo.ps1
```

The launcher will:

- start the FastAPI backend from `backend/`
- start the Next.js frontend from `frontend/`
- open `http://localhost:3000`
- keep backend and frontend in separate terminal windows where errors remain visible

Tesseract is not required. It remains optional, disabled by default, and policy-gated.

## Stop The Demo

From the repository root, double-click:

```text
stop-pharmaguard-demo.bat
```

Or run:

```powershell
.\stop-pharmaguard-demo.ps1
```

The stop script looks for listeners on ports `3000` and `8000` and stops them. If terminal windows are still open, close them manually.

## Manual Launch Fallback

Backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
```

Use `npm.cmd` on Windows if PowerShell blocks `npm.ps1`.

## Pages To Open

- Main dashboard: `http://localhost:3000`
- Evidence page: `http://localhost:3000/evaluation`
- Backend health: `http://localhost:8000/health`
- Presentation: `docs/presentation.html`

## Demo Flow

1. Open the dashboard.
2. Show the header safety badges and command-center hero.
3. Use `Load sample` in the prescription text card.
4. Select `Analyze text`.
5. Inspect pharmacist review, safety review, source grounding, and KB context.
6. Generate a counseling draft only after pharmacist confirmation.
7. Open `/evaluation` to show synthetic engineering evidence.

## Safety Boundaries

- Prototype only.
- Synthetic data only.
- Not clinical validation.
- Not a medical device.
- Pharmacist review required.
- Patient-facing final advice disabled.
- Current KB is draft placeholder educational content.
- Do not use real prescriptions or real patient data.

## Pre-Demo Health Check

Run:

```powershell
cd backend
python scripts/demo_health_check.py
```

This checks key files, brand assets, final demo cases, and backend import sanity without requiring services to be running.
