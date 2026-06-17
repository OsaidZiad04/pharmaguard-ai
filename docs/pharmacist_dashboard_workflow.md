# Pharmacist Dashboard Workflow

Phase 2I polishes the pharmacist dashboard so the safe workflow is visible without changing backend behavior.

## Workflow Steps

The dashboard now presents the workflow as ordered status steps:

- OCR Intake
- Pharmacist Correction
- Prescription Analysis
- Medication Extraction
- RAG Source Check
- Counseling Draft
- Pharmacist Review

Each step can show `waiting`, `required`, `ready`, `completed`, or `blocked`.

## Safety Indicators

The dashboard includes compact indicators for:

- OCR unverified
- correction required
- corrected text ready
- possible identifier warnings
- RAG sources available
- insufficient knowledge-base context
- counseling draft-only status
- pharmacist review required

These indicators are derived from existing frontend state and backend responses. They do not introduce a new backend workflow or bypass any safety gates.

## Correction Boundary

The OCR card makes the correction boundary explicit:

- OCR output is unverified.
- OCR output cannot move downstream automatically.
- The pharmacist must confirm or correct OCR text.
- Only corrected text can populate the prescription text panel.

## Source Grounding

The source grounding panel summarizes retrieved local Markdown context:

- retrieved chunk count
- source file count
- section count
- insufficient-context warning state
- source/review/clinical-validation status when returned by the backend

RAG source display remains local, draft-only, and pharmacist-review-required. Phase 3A adds compact governance indicators so the dashboard can show when retrieved chunks are placeholder educational content and not clinically validated.

## Scope Boundaries

This phase does not add real OCR, activate Tesseract, call external APIs, store prescription images, add real patient data, or claim clinical validation.

Phase 2J adds only an optional backend benchmark command for the disabled Tesseract adapter. The dashboard continues to use the existing safe OCR workflow and does not expose Tesseract as an active provider.

Phase 2L-M adds backend OCR activation policy. The dashboard still defaults to the existing safe OCR workflow. If a future UI exposes provider status, it must show blocked/allowed policy state clearly and must not let unverified OCR text bypass pharmacist correction.

Phase 3B-C adds backend retrieval diagnostics and medication safety-rule findings. The dashboard can display these as compact pharmacist-review prompts in a future polish pass, but they must not be shown as final medical advice or as proof that a prescription is clinically appropriate.

## Phase 4-Final Evaluation Page

Phase 4-Final adds a static `/evaluation` page for portfolio review. It summarizes engineering evidence such as RAG, OCR, E2E, KB governance, safety rules, and Tesseract policy status. The page is intentionally static and does not claim clinical validation, production readiness, or patient-facing approval.

## Brand And Bilingual-Ready Polish

The dashboard now uses PharmaGuard AI brand assets from `frontend/public/brand/`:

- `/brand/pharmaguard-logo-main.png`
- `/brand/pharmaguard-logo-icon.png`
- `/brand/pharmaguard-hero-visual.png`

The visual system uses flexible cards, wrapping badges, and an EN/AR placeholder so future Arabic/RTL support can be added without redesigning the workflow. No translation system is active yet.
