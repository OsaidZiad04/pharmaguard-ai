# PharmaGuard AI

PharmaGuard AI is a pharmacist-centered AI copilot foundation for prescription text review, trusted medication information retrieval, patient counseling note drafting, and safety-first workflow enforcement.

This repository is intentionally scoped as a scaffolding/MVP foundation. It uses synthetic data and local placeholder knowledge only. It is not a medical device, does not diagnose, and must never make final medical decisions.

## Problem Statement

Pharmacists often need to interpret incomplete prescription text, verify medication context, identify missing patient details, and prepare clear counseling notes under time pressure. AI can help organize information, but unsafe automation can introduce risk if it appears to replace professional judgment.

## Solution

PharmaGuard AI is designed as a review-first copilot:

- Extract possible medication entities from prescription text.
- Retrieve local trusted medication profile placeholders through a Phase 1 TF-IDF RAG workflow.
- Surface missing patient context and confidence warnings.
- Require pharmacist confirmation before generating counseling notes.
- Keep every output framed as a draft for pharmacist review.

## Architecture

Current scaffold:

- `backend/`: FastAPI API, services, schemas, tests, and local RAG modules.
- `frontend/`: Next.js pharmacist dashboard with Tailwind CSS.
- `data/`: synthetic prescriptions, draft drug profiles, the drug registry, and evaluation templates.
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
- Local Markdown drug knowledge base.
- Phase 1 local TF-IDF RAG: Markdown loading, chunking, in-memory indexing, retrieval, and grounded draft generation.
- Phase 1.5 RAG hardening: synthetic RAG evaluation cases, citation validation, unsupported-claim regression tests, and a CLI evaluation runner.
- Phase 1.6 knowledge base and evaluation expansion: seven local drug profiles and 20 synthetic RAG evaluation cases.
- Phase 1.7 controlled knowledge base expansion: 15 local drug profiles and 46 synthetic RAG evaluation cases.
- Phase 1.8 scalable knowledge base architecture: structured drug registry, KB validation, coverage reporting, and safe future ingestion stubs.
- Direct `POST /rag/query` endpoint.
- Next.js dashboard that calls backend endpoints.
- Pytest coverage for core placeholder behavior, RAG retrieval, citation validation, KB registry validation, and safety regressions.

Not implemented yet:

- OCR.
- External medical APIs.
- Dense embeddings or persistent vector database.
- Production clinical validation.
- Real patient data handling.

## Supported Local Knowledge Base

Current local Markdown profiles:

- paracetamol
- ibuprofen
- amoxicillin
- cetirizine
- loratadine
- omeprazole
- salbutamol
- metformin
- amlodipine
- levothyroxine
- azithromycin
- simvastatin
- diclofenac
- esomeprazole
- aspirin

`data/drug_profiles/drug_registry.json` is now the preferred source of truth for supported generic names, aliases, review status, source status, and whether a profile is enabled for local RAG. All 15 current profiles are marked `review_status: draft` and `source_status: placeholder_educational`; this makes clear that the current content is educational placeholder material, not clinical validation.

Supported aliases are explicit and conservative, such as `acetaminophen -> paracetamol`, `ventolin -> salbutamol`, `glucophage -> metformin`, `norvasc -> amlodipine`, `synthroid -> levothyroxine`, `voltaren -> diclofenac`, and `nexium -> esomeprazole`. Condition-only queries and broad classes such as `antibiotic`, `painkiller`, or `antihistamine` do not map to a medication.

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

Example local RAG query:

```bash
curl -X POST http://localhost:8000/rag/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"paracetamol 500mg counseling\",\"top_k\":5}"
```

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
python -m pytest
```

Run the local RAG evaluation:

```bash
cd backend
python scripts/evaluate_rag.py
```

Run the local knowledge-base coverage report:

```bash
cd backend
python scripts/kb_report.py
```

The evaluation currently contains 46 synthetic cases. It reports retrieval checks (`top_k_hit`, `source_file_hit`, `section_hit`, `insufficient_context_correct`) and generation safety checks for required terms, forbidden terms, draft/pharmacist-review framing, unavailable information, and fabricated citations.

The KB report summarizes profile counts, aliases, review/source status, missing sections, alias conflicts, disabled profiles, and unreviewed draft profiles. Dense retrieval remains deferred until the TF-IDF baseline and KB governance are stronger. OCR remains Phase 2 and is intentionally not implemented in Phase 1.8.

## Future Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Data Warning

Only synthetic prescriptions are allowed in this repository. Do not commit patient names, phone numbers, IDs, addresses, clinic identifiers, prescription images, or any other real patient information.
