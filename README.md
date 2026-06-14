# PharmaGuard AI

PharmaGuard AI is a pharmacist-centered AI copilot foundation for prescription text review, trusted medication information retrieval, patient counseling note drafting, and safety-first workflow enforcement.

This repository is intentionally scoped as a scaffolding/MVP foundation. It uses mock logic, synthetic data, and local placeholder knowledge only. It is not a medical device, does not diagnose, and must never make final medical decisions.

## Problem Statement

Pharmacists often need to interpret incomplete prescription text, verify medication context, identify missing patient details, and prepare clear counseling notes under time pressure. AI can help organize information, but unsafe automation can introduce risk if it appears to replace professional judgment.

## Solution

PharmaGuard AI is designed as a review-first copilot:

- Extract possible medication entities from prescription text.
- Retrieve local trusted medication profile placeholders through a future RAG workflow.
- Surface missing patient context and confidence warnings.
- Require pharmacist confirmation before generating counseling notes.
- Keep every output framed as a draft for pharmacist review.

## Architecture

Current scaffold:

- `backend/`: FastAPI API, services, schemas, tests, and RAG module skeletons.
- `frontend/`: Next.js pharmacist dashboard with Tailwind CSS.
- `data/`: synthetic prescriptions, mock drug profiles, and evaluation templates.
- `docs/`: architecture, safety, privacy, roadmap, and challenge planning documents.

Planned pipeline:

`Prescription Input -> OCR later -> Text Extraction -> Drug Entity Extraction -> Safety Layer -> RAG Retrieval -> Pharmacist Review -> Patient Counseling`

## Safety-First Principles

- Pharmacist stays in control.
- AI output is draft support only.
- Low confidence always requires review.
- Unknown medication names are not guessed.
- Missing age, pregnancy status, allergies, or current medication context triggers a warning.
- No real patient data belongs in this repository.

## Current MVP Scope

Implemented now:

- FastAPI app with health, prescription analysis, drug lookup, and counseling endpoints.
- Mock extraction and safety services.
- Local mock drug index.
- RAG class/function skeletons with TODO markers.
- Next.js dashboard that calls backend endpoints.
- Pytest coverage for core placeholder behavior.

Not implemented yet:

- OCR.
- External medical APIs.
- Real embeddings or vector database.
- Production clinical validation.
- Real patient data handling.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/health`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` if the backend runs on a different host or port.

## Testing

```bash
cd backend
pytest
```

## Future Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Data Warning

Only synthetic prescriptions are allowed in this repository. Do not commit patient names, phone numbers, IDs, addresses, clinic identifiers, prescription images, or any other real patient information.
