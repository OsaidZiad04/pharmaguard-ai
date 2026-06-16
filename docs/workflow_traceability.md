# Workflow Traceability

Phase 2H adds structured trace records for the safe pharmacist-in-the-loop workflow. These traces are engineering audit artifacts for synthetic evaluation, not clinical validation.

## Purpose

Workflow traces explain what happened at each step:

- OCR-like input was captured as unverified
- unverified OCR was blocked from downstream use
- pharmacist correction was required
- corrected text became the downstream analysis boundary
- prescription analysis and medication extraction ran on corrected text
- RAG sources were checked
- counseling drafts remained pharmacist-support only
- pharmacist review remained required

## Trace Structure

The trace schema lives in:

`backend/app/workflows/trace.py`

Main records:

- `WorkflowTrace`
- `WorkflowTraceStep`
- `WorkflowSafetyFlag`
- `PharmacistReviewRecord`

Each trace includes:

- deterministic `trace_id`
- `case_id`
- `created_at`
- `input_mode`
- `provider_name`
- step records
- safety flags
- pharmacist review record
- `contains_real_patient_data: false`
- `stores_raw_image_bytes: false`
- final status

## What Is Recorded

Traces record:

- workflow step names and statuses
- reference types, not raw payloads
- source filenames for retrieved local Markdown context
- safety notes
- possible identifier categories
- pharmacist correction/review status

## What Is Not Recorded

Traces do not record:

- raw image bytes
- real prescription images
- real patient identifiers
- production audit logs
- final medical advice
- real clinical decisions

Synthetic traces intentionally avoid raw OCR text and corrected text payloads. They store summaries and reference types only.

## Generated Trace Policy

Generated synthetic traces are written to:

`data/evaluation/generated/e2e_traces.json`

The file is deterministic, small, and synthetic, so it is committed as an evaluation artifact. Regenerate it from `backend/` with:

```bash
python scripts/export_e2e_traces.py
```

Trace reports can be generated with:

```bash
python scripts/e2e_trace_report.py
```

## Safety Boundary

Traceability does not change runtime behavior. It does not make OCR automatic, does not activate Tesseract, does not call external APIs, and does not add persistent production storage.

Corrected pharmacist text remains the boundary for downstream prescription analysis. Pharmacist review remains mandatory for clinical-facing output.
