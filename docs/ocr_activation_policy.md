# OCR Activation Policy

Phase 2L-M adds controlled activation policy for OCR providers. This is a safety and governance boundary, not production OCR approval.

## Safe Defaults

The backend reads optional environment variables but does not require `.env`:

```bash
PHARMAGUARD_OCR_DEFAULT_PROVIDER=mock_ocr_phase_2a
PHARMAGUARD_OCR_MODE=default_workflow
PHARMAGUARD_ENABLE_TESSERACT_PROTOTYPE=false
PHARMAGUARD_ALLOW_EXTERNAL_OCR=false
PHARMAGUARD_TESSERACT_BENCHMARK_PASSED=false
```

With no environment variables, the default OCR provider remains `mock_ocr_phase_2a`.

## Modes

- `default_workflow`: normal upload workflow. Mock OCR remains allowed. Tesseract is blocked.
- `benchmark`: local benchmark path only. Tesseract can be benchmarked if dependencies are available.
- `prototype_explicit`: opt-in local Tesseract workflow mode. It requires explicit enablement, available dependencies, and a recorded passing synthetic benchmark.
- `production`: blocked for current OCR providers. No provider is clinically or production validated.

## Provider Policy

`mock_ocr_phase_2a`:

- allowed in default workflow
- local, non-networked, non-storing
- correction gate required
- not production validated

`synthetic_fixture_phase_2c`:

- allowed for synthetic evaluation and tests
- local, non-networked, non-storing
- correction gate required
- not production validated

`tesseract_local_candidate`:

- blocked in default workflow
- allowed in benchmark mode only when dependencies are available
- allowed in `prototype_explicit` only when all policy gates pass
- not default
- not production allowed
- correction gate required

Cloud OCR candidates:

- blocked in current prototype modes
- no external OCR APIs are called

## Correction Gate

Every OCR provider result remains:

- unverified
- correction-required
- not sendable to prescription analysis until pharmacist confirmation
- disconnected from RAG, lookup, and counseling until corrected text is explicitly submitted

## Report

Run:

```bash
cd backend
python scripts/ocr_activation_policy_report.py
```

The report shows provider policies, configured mode, environment flags, allowed modes, blocking reasons, warnings, and correction gate requirements.

The policy report is engineering governance only. It is not clinical validation.
