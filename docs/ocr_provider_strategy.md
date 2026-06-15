# OCR Provider Strategy

Phase 2C prepares PharmaGuard AI for future OCR provider integration without adding production OCR or external APIs.

## Current Providers

The current provider interface is defined in `backend/app/ocr/providers.py`.

Available providers:

- `mock_ocr_phase_2a`
- `synthetic_fixture_phase_2c`

Both current providers are:

- local
- deterministic
- non-external
- non-networked
- non-storing
- pharmacist-review required

Phase 2F also defines an inactive adapter skeleton:

- `tesseract_local_candidate`

The Tesseract adapter is disabled by default, not prototype-allowed, and not part of the active OCR flow.

## Provider Metadata

Every provider exposes:

- `provider_name`
- `extract_text(file_bytes, filename, content_type)`
- `supports_content_type(content_type)`
- `is_external_provider`
- `stores_images`
- `requires_network`
- `requires_system_dependency`
- `enabled_by_default`
- `prototype_allowed`
- `supported_content_types`

The OCR API response includes provider metadata so the frontend and future audit layers can show whether an OCR result came from a local mock, a synthetic fixture provider, or a future approved provider.

## Synthetic Fixture Provider

`SyntheticFixtureOcrProvider` maps known synthetic fixture filenames to deterministic OCR text. It supports fixture-backed evaluation without adding a real OCR engine.

Current fixture directory:

`data/evaluation/ocr_fixtures/`

Current fixtures:

- `synthetic_paracetamol_clean.png`
- `synthetic_ibuprofen_noisy.png`
- `synthetic_amoxicillin_possible_identifier.png`
- `synthetic_no_medication.png`

These fixtures are synthetic engineering assets only. They contain no real patient data and are not clinical validation.

## Provider Report

Run from `backend/`:

```bash
python scripts/ocr_provider_report.py
```

The report lists provider names, safety metadata, supported content types, and whether each provider is allowed in current prototype mode.

Phase 2D adds quality gate eligibility to the provider report. Current provider eligibility requires:

- local/non-external provider
- no network requirement
- no image storage
- synthetic benchmark metrics within thresholds
- medication detection checks passing
- privacy warning checks passing
- unverified output status preserved

These gates are provider swap-readiness checks, not clinical validation.

Phase 2F extends the provider report with inactive adapter status and dependency availability. Tesseract appears as adapter-defined but inactive; it is blocked unless dependency checks, explicit enablement, and quality gates pass in a future phase.

## Candidate Comparison

Phase 2E adds a candidate registry at `data/evaluation/ocr_provider_candidates.json`.

The current matrix includes:

- implemented mock provider
- implemented synthetic fixture provider
- planned Tesseract local candidate
- planned EasyOCR local candidate
- cloud OCR placeholder disallowed for prototype mode

Run from `backend/`:

```bash
python scripts/ocr_candidate_report.py
```

The candidate report is metadata-only. It does not install dependencies, call external APIs, or process real images. Phase 2F adds an inactive Tesseract adapter skeleton, but it remains disabled and is not used for extraction.

## Future Provider Requirements

A future real OCR provider must pass the same boundary:

- OCR output remains unverified.
- Pharmacist correction remains mandatory.
- Uploaded images are not stored unless a future privacy-approved storage layer exists.
- External providers must not be enabled without explicit privacy and security review.
- Possible identifiers remain warnings, not confirmed PII.
- OCR output must not automatically trigger prescription analysis, RAG, lookup, or counseling.
- Provider quality metrics remain engineering checks, not clinical validation.
