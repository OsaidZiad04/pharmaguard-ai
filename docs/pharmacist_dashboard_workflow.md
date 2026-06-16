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

RAG source display remains local, draft-only, and pharmacist-reviewed.

## Scope Boundaries

This phase does not add real OCR, activate Tesseract, call external APIs, store prescription images, add real patient data, or claim clinical validation.

Phase 2J adds only an optional backend benchmark command for the disabled Tesseract adapter. The dashboard continues to use the existing safe OCR workflow and does not expose Tesseract as an active provider.
