# End-to-End OCR-to-RAG Workflow Evaluation

Phase 2G adds synthetic workflow evaluation for the safe OCR-to-RAG path. It verifies that OCR output stays unverified, pharmacist correction is the downstream boundary, and RAG/counseling outputs remain source-grounded pharmacist-support drafts.

This is not clinical validation. It uses synthetic text and approved synthetic fixture filenames only.

## Scope

The evaluator covers:

- OCR-like text input or synthetic fixture OCR input
- unverified OCR status
- pharmacist correction
- prescription text analysis
- medication extraction
- supported and unsupported medication handling
- local RAG retrieval
- counseling draft generation after corrected text only
- privacy warning propagation
- pharmacist review-required status

It does not:

- run real OCR
- activate Tesseract
- call external APIs
- store images
- use real prescriptions or real patient data
- automatically send unverified OCR output downstream

## Evaluation Data

Synthetic cases live in:

`data/evaluation/e2e_workflow_cases.json`

Current coverage includes:

- clean supported single medication
- noisy OCR corrected to a supported medication
- multiple supported medications
- supported plus unsupported medication-like text
- unknown medication only
- possible identifier warning
- no medication detected
- exact-dose request
- final-advice request
- fixture-backed synthetic OCR case

## Evaluator

The evaluator lives in:

`backend/app/workflows/e2e_evaluation.py`

It calls existing service boundaries directly. It uses corrected pharmacist text for downstream analysis and keeps the original OCR text as unverified evaluation input only.

Returned checks include:

- privacy warning status
- medication extraction status
- RAG source grounding status
- counseling generation status
- safety status
- pharmacist review-required status
- synthetic workflow trace record

## Runner

Run from `backend/`:

```bash
python scripts/evaluate_e2e_workflow.py
```

The report prints total, passed, and failed cases plus summaries for privacy warnings, medication extraction, RAG grounding, counseling generation, safety, and pharmacist review.

## Safety Boundary

Corrected text is the only boundary that can move into prescription analysis. Unverified OCR text is never treated as final truth and does not automatically trigger RAG, counseling, lookup, or prescription analysis.

## Traceability

Phase 2H adds trace records for each synthetic E2E case. Each trace records step status, source refs, safety notes, safety flags, and pharmacist review status.

Trace records show:

- OCR output is unverified
- unverified OCR downstream use is blocked
- pharmacist correction is required
- corrected text is used for analysis
- RAG sources are checked
- counseling drafts remain draft support only
- pharmacist review is required

The generated trace file is:

`data/evaluation/generated/e2e_traces.json`

Regenerate it from `backend/`:

```bash
python scripts/export_e2e_traces.py
```

The trace file is deterministic and synthetic. It does not store raw image bytes, real prescription data, or real patient identifiers.
