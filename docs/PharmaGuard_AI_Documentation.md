# PharmaGuard AI Documentation

## Project Overview

PharmaGuard AI is a pharmacist-centered AI copilot prototype for prescription workflow support. It demonstrates OCR intake, pharmacist correction, local source-grounded RAG, knowledge-base governance, deterministic safety prompts, traceability, and synthetic evaluation.

The project is prototype-only. It is not a medical device, not clinically validated, not a patient-facing medical advisor, and not a replacement for pharmacists. Pharmacist review remains mandatory.

## Architecture

The system is organized into three main layers:

- **Frontend:** Next.js, TypeScript, and Tailwind pharmacist dashboard.
- **Backend:** FastAPI services for OCR intake, prescription analysis, drug lookup, RAG retrieval, counseling draft generation, safety findings, and reporting scripts.
- **Data:** Local Markdown drug profiles, governed drug registry, source catalog, synthetic OCR fixtures, and synthetic evaluation datasets.

Current workflow:

1. Prescription text input or synthetic prescription image upload.
2. OCR extraction if image input is used.
3. OCR output is marked unverified.
4. Pharmacist correction or confirmation is required.
5. Corrected text can be sent to prescription analysis.
6. Medication extraction runs.
7. Local RAG retrieves Markdown context and source metadata.
8. Safety rules and KB governance warnings are surfaced.
9. Counseling output remains draft-only and pharmacist-review-required.

## Key Features

- Privacy-safe OCR intake foundation.
- Mock and synthetic OCR providers as safe defaults.
- Optional local Tesseract adapter and benchmark path, disabled by default.
- Pharmacist correction gate before downstream analysis.
- Local TF-IDF RAG over Markdown drug profiles.
- Source metadata and governance badges for retrieved chunks.
- Knowledge-base registry and source catalog.
- Retrieval diagnostics and retrieval strategy comparison.
- Deterministic medication safety-rule findings.
- Synthetic E2E workflow evaluation and trace export.
- Static `/evaluation` portfolio evidence dashboard.
- Premium branded pharmacist command-center UI.
- Visual EN/AR placeholder for future bilingual support.

## Safety Design

PharmaGuard AI is designed around safety boundaries:

- Pharmacist review is mandatory.
- Outputs are draft support only.
- Patient-facing final advice is disabled.
- OCR output is unverified.
- Raw OCR cannot automatically trigger prescription analysis, RAG, lookup, or counseling.
- Unknown or weak-context medications return insufficient knowledge-base context.
- Current drug profiles are draft placeholder educational content.
- No profile is clinically validated.
- No real interaction, contraindication, diagnosis, treatment-selection, or patient-specific appropriateness engine is implemented.
- Possible identifiers are warnings only, not confirmed PII determinations.
- No real patient data belongs in this repository.

## Knowledge Base

The current local knowledge base contains 15 draft profiles:

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

All profiles currently have:

- `review_status: draft`
- `source_status: placeholder_educational`
- `clinical_validation_status: not_validated`
- `requires_pharmacist_review: true`
- `patient_facing_allowed: false`
- `counseling_draft_allowed: true`

## Evaluation Results

Latest documented synthetic engineering results:

- Backend tests: 177 passed, 1 skipped.
- RAG evaluation: 46/46 passed.
- OCR evaluation: 18/18 passed.
- E2E OCR-to-RAG workflow evaluation: 10/10 passed.
- Retrieval strategy evaluation: PASS, `existing_default` remains recommended.
- KB report: PASS, 15 profiles, 0 blockers.
- KB governance report: PASS, 0 blockers with expected draft warnings.
- Safety rules report: PASS, 10/10 synthetic scenarios.
- OCR provider/candidate/activation reports: PASS.
- Tesseract benchmark: optional; completes or safely skips when local dependency is unavailable.
- Frontend typecheck/build: PASS.

These are engineering checks using synthetic data. They are not clinical validation.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
http://localhost:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```bash
http://localhost:3000
```

Evaluation page:

```bash
http://localhost:3000/evaluation
```

## Demo Cases

Final synthetic demo cases live in:

```bash
data/evaluation/final_demo_cases.json
```

They cover:

- Clean single-medication prescription.
- OCR correction boundary.
- Missing dose or frequency prompt.
- Multiple medications.
- Unsupported medication.
- Possible identifier warning.
- Insufficient KB context.

Run the final demo report:

```bash
cd backend
python scripts/final_demo_report.py
```

## Useful Verification Commands

```bash
cd frontend
npm.cmd run typecheck
npm.cmd run build
```

```bash
cd backend
python -m pytest
python scripts/project_evidence_report.py
python scripts/final_demo_report.py
```

```bash
git diff --check
```

## Limitations

- Prototype only.
- Not clinically validated.
- Not a medical device.
- Not a patient-facing advisor.
- Does not replace pharmacists.
- No real patient data.
- No trusted clinical source ingestion yet.
- No production OCR default.
- No cloud OCR.
- No production database or authentication.
- No clinical interaction or contraindication engine.
- Current KB is draft placeholder educational content.

## Future Work

- Trusted-source ingestion with provenance.
- Pharmacist review and sign-off workflow.
- Production privacy, access control, and audit-retention design.
- Expanded bilingual Arabic/RTL support.
- Knowledge graph experiments after source governance is stronger.
- Deployment hardening only after privacy and validation planning.

## PDF Export Instructions

A generated PDF is not committed in this phase because no lightweight PDF export tool is guaranteed in the repository.

To create a PDF without adding dependencies:

1. Open this Markdown file in VS Code or a Markdown preview tool.
2. Export or print to PDF using the editor/browser print dialog.
3. Name the file `PharmaGuard_AI_Documentation.pdf`.
4. Confirm the PDF does not include real patient data or clinical-validation claims before sharing.
