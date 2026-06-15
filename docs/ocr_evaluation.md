# OCR Evaluation And Correction Audit

Phase 2B adds a local evaluation and audit layer around the Phase 2A OCR intake boundary.
Phase 2C extends this with fixture-backed cases through the local `SyntheticFixtureOcrProvider`. Phase 2D adds provider-specific quality gates and expanded synthetic fixture coverage.

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

Phase 2C and Phase 2D cases can also include `fixture_filename`, which points to an approved synthetic PNG or descriptor fixture in `data/evaluation/ocr_fixtures/`. Fixture-backed cases use `SyntheticFixtureOcrProvider` to produce deterministic OCR text from the filename.

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

The script also reports text-only cases, fixture-backed cases, and provider used.

Phase 2D output also includes provider-level summaries and quality gate status.

## Quality Gates

`backend/app/ocr/quality_gates.py` checks:

- maximum average character error rate for the synthetic benchmark
- maximum average word error rate for the synthetic benchmark
- minimum average token overlap
- medication detection pass/fail count
- privacy warning pass/fail count
- provider must be non-networked in prototype mode
- provider must not store images in prototype mode
- provider output must remain unverified

Identifier-heavy privacy cases still enforce privacy-warning matching. CER/WER gates are calculated over OCR quality metric cases so intentional privacy removal does not incorrectly fail a provider.

## Provider Report

Run from `backend/`:

```bash
python scripts/ocr_provider_report.py
```

The report lists available local OCR providers, whether they are external, whether they store images, whether they require network access, supported content types, and whether each provider is allowed in current prototype mode.

## Future Boundary

Any future OCR provider must pass this boundary before being considered for workflow use:

- output remains unverified
- pharmacist correction remains required
- possible identifiers remain warnings, not confirmed PII
- no automatic handoff to RAG, counseling, lookup, or prescription analysis
- no image storage without explicit privacy controls
