# OCR Evaluation And Correction Audit

Phase 2B adds a local evaluation and audit layer around the Phase 2A OCR intake boundary.

## Scope

- Synthetic OCR evaluation cases only.
- Deterministic text metrics only.
- No production OCR engine.
- No external OCR APIs.
- No real prescription images.
- No persistent audit database.

OCR remains an assistive input layer. OCR output is unverified until a pharmacist corrects it.

## Evaluation Data

`data/evaluation/ocr_eval_cases.json` contains synthetic text fixtures with:

- mock OCR text
- expected corrected text
- expected medication terms
- expected possible identifier categories
- expected privacy warning count
- difficulty level
- notes

The dataset intentionally includes supported medications, unsupported medication names, noisy text, possible identifier labels, and no-medication cases.

## Metrics

`backend/app/ocr/evaluation.py` provides:

- `character_error_rate(reference, prediction)`
- `word_error_rate(reference, prediction)`
- `token_overlap_score(reference, prediction)`
- `medication_detection_hit(expected_medications, text)`
- `privacy_warning_match(expected_identifiers, detected_identifiers)`

These metrics are engineering regression checks. They are not clinical validation and should not be used to claim OCR production readiness.

## Correction Audit

`backend/app/services/ocr_audit_service.py` returns audit metadata from `/ocr/confirm-text`:

- original OCR text
- pharmacist-corrected text
- changed/unchanged status
- correction summary
- character and word error rates
- detected supported medication terms
- possible identifier warning categories
- generated timestamp

The audit is returned in the API response only. It is not stored in a database in Phase 2B.

## Runner

Run from `backend/`:

```bash
python scripts/evaluate_ocr.py
```

The script prints total cases, passed cases, failed cases, average character error rate, average word error rate, medication detection summary, privacy warning summary, and per-case status.

## Future Boundary

Any future OCR provider must pass this boundary before being considered for workflow use:

- output remains unverified
- pharmacist correction remains required
- possible identifiers remain warnings, not confirmed PII
- no automatic handoff to RAG, counseling, lookup, or prescription analysis
- no image storage without explicit privacy controls
