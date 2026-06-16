# Final QA Checklist

## Pre-Demo Checklist

- Run `python backend/scripts/final_project_qa.py`.
- Confirm frontend builds.
- Confirm backend tests pass.
- Confirm RAG, OCR, E2E, KB, governance, retrieval, safety, and trace reports pass.
- Use only synthetic demo cases.
- Prepare a fallback line for Tesseract skip.
- Open dashboard and optional evaluation page.
- State project limitations clearly.

## Pre-Commit Checklist

- Run `git diff --check`.
- Confirm no real patient data or prescription images are present.
- Confirm generated traces remain synthetic.
- Confirm no `.env` or private data files are staged.
- Confirm current KB profiles remain draft and not clinically validated.

## Pre-Push Checklist

- Read README from a new visitor's perspective.
- Confirm setup instructions work.
- Confirm final docs are linked.
- Confirm known limitations are visible.
- Confirm no overclaiming language was added.

## Known Limitations Checklist

- No clinical validation.
- No real trusted-source ingestion.
- No production OCR.
- No patient-facing output.
- No drug-drug interaction engine.
- No contraindication engine.
- No production authentication or audit database.
