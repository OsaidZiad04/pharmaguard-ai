# Local Tesseract OCR Benchmarking

Phase 2J adds an optional benchmark path for the disabled local Tesseract OCR adapter. This phase does not make Tesseract the default provider and does not allow unverified OCR output to bypass pharmacist correction.

## Scope

- Synthetic PNG fixtures only.
- Optional local Tesseract dependencies only.
- No cloud OCR.
- No external OCR APIs.
- No real prescription images.
- No real patient data.
- No uploaded image storage.
- No automatic handoff to prescription analysis, RAG, lookup, or counseling.

Benchmark results are engineering readiness signals only. They are not clinical validation.

## Provider Status

`TesseractLocalOcrProvider` remains:

- `enabled_by_default: false`
- `prototype_allowed: false`
- `benchmark_only: true`
- local and non-networked
- non-storing
- unverified-output only
- pharmacist-correction required

The default OCR providers remain `mock_ocr_phase_2a` and `synthetic_fixture_phase_2c`.

## Dependencies

The project does not install Tesseract or `pytesseract`.

To benchmark locally, install outside the project environment:

- Tesseract OCR system binary
- Python package `pytesseract`
- Pillow

The repository must still run when these dependencies are missing.

Check provider status:

```bash
cd backend
python scripts/ocr_provider_report.py
python scripts/ocr_candidate_report.py
```

## Benchmark Runner

Run:

```bash
cd backend
python scripts/benchmark_tesseract_ocr.py
```

The runner:

- loads fixture-backed OCR evaluation cases
- runs only image fixtures such as `.png`, `.jpg`, `.jpeg`, and `.webp`
- skips descriptor fixtures such as `.fixture.md`
- compares Tesseract output against expected pharmacist-corrected text
- computes character error rate, word error rate, token overlap, medication detection, and privacy warning checks
- applies OCR quality gates
- exits successfully if Tesseract is unavailable because this benchmark is optional

## Interpretation

A passing benchmark does not make Tesseract production-ready. A future policy change would still require:

- explicit activation decision
- privacy review
- dependency and deployment review
- stronger synthetic and workflow evaluation
- pharmacist correction remaining mandatory
- no automatic downstream use of unverified OCR

A failing benchmark means the local adapter is not ready for workflow use. It should remain disabled.
