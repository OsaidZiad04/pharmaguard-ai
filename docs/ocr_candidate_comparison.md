# OCR Candidate Comparison

Phase 2E adds a metadata-only comparison layer for future OCR provider candidates. No production OCR provider is integrated, installed, instantiated, or called in this phase.

## Candidate Registry

Candidate metadata lives in:

`data/evaluation/ocr_provider_candidates.json`

Current candidates:

- `mock_ocr_phase_2a`
- `synthetic_fixture_phase_2c`
- `tesseract_local_candidate`
- `easyocr_local_candidate`
- `cloud_ocr_candidate_placeholder`

The implemented providers are allowed in prototype mode because they are local, non-networked, non-storing, and already pass the current synthetic OCR quality gates.

The Tesseract and EasyOCR entries are planned local candidates. Phase 2F adds a disabled Tesseract adapter skeleton, but it is not installed as a working OCR engine and is not active. EasyOCR remains metadata-only. The cloud OCR placeholder is disallowed for prototype mode because it requires network access and may involve image storage or external processing.

## Candidate Fields

Each candidate records:

- provider identity and display name
- provider type
- current status
- network, storage, dependency, and model-download requirements
- expected privacy risk
- prototype allowed status
- production possible after review status
- required quality gates
- required privacy controls
- integration blockers

## Swap Readiness

`backend/app/ocr/provider_swap_readiness.py` checks whether a candidate:

- exposes an active `BaseOcrProvider` adapter
- returns provider metadata
- marks OCR output as unverified
- requires pharmacist correction before analysis
- avoids automatic downstream analysis
- passes OCR quality gates before use
- declares privacy properties
- is blocked in prototype mode if networked or image-storing
- is blocked if optional local dependencies are missing or the adapter is disabled by default

## Candidate Report

Run from `backend/`:

```bash
python scripts/ocr_candidate_report.py
```

The report prints candidate counts, prototype eligibility, network/storage/dependency requirements, dependency status, and per-candidate readiness.

## Policy

Candidate comparison is an engineering readiness tool, not clinical validation. Future OCR providers must pass privacy, workflow, and synthetic benchmark gates before they can be considered for pharmacist workflow evaluation. OCR output remains unverified until pharmacist correction.
