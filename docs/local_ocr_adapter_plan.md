# Local OCR Adapter Plan

Phase 2F adds a disabled-by-default adapter skeleton for a future local Tesseract OCR provider. This is integration scaffolding only. It does not install Tesseract, install `pytesseract`, activate real OCR, store images, or bypass pharmacist correction.

## Current Adapter

`backend/app/ocr/local_tesseract_provider.py` defines `TesseractLocalOcrProvider` behind the existing `BaseOcrProvider` interface.

Current metadata:

- `provider_name`: `tesseract_local_candidate`
- `is_external_provider`: `false`
- `stores_images`: `false`
- `requires_network`: `false`
- `requires_system_dependency`: `true`
- `enabled_by_default`: `false`
- `prototype_allowed`: `false`

The provider raises a controlled unavailable error when extraction is requested. It is not part of the default OCR flow.

## Dependency Checks

`backend/app/ocr/provider_dependencies.py` checks local dependency availability without installing anything or calling the network.

Current checks:

- `check_python_package_available("pytesseract")`
- `check_tesseract_available()`
- `get_provider_dependency_status("tesseract_local_candidate")`

Missing dependencies must not crash the app or tests.

## Activation Requirements

Before any future activation, a local OCR provider must:

- remain non-networked and non-storing
- expose the `BaseOcrProvider` interface
- return provider metadata
- mark OCR output as unverified
- require pharmacist correction before analysis
- pass synthetic OCR quality gates
- pass privacy warning checks
- document installation and patching constraints
- avoid automatic handoff to prescription analysis, RAG, counseling, or lookup

## Current Policy

Mock and synthetic fixture providers remain the only active prototype OCR providers. Tesseract is adapter-defined but inactive. EasyOCR remains metadata-only. Cloud OCR remains blocked for prototype mode.

OCR metrics are engineering checks only. They are not clinical validation.
