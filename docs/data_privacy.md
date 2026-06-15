# Data Privacy

This repository must not contain real patient data.

## Prohibited Data

Do not commit:

- patient names
- phone numbers
- addresses
- national IDs or insurance IDs
- prescription numbers
- clinic, prescriber, or pharmacy identifiers
- dates of birth
- prescription images containing real information
- free text that could identify a patient or clinic

## Synthetic Data Only

Use synthetic examples that are clearly fictional. The examples in `data/sample_prescriptions/synthetic_cases.json` are fabricated for software testing.

The local drug profiles and `data/drug_profiles/drug_registry.json` contain educational placeholder knowledge-base metadata only. They must not contain patient identifiers, clinic identifiers, real prescription details, or claims of clinical validation.

## Real Prescription Handling

If real prescriptions are ever used for local experimentation:

1. Remove direct identifiers.
2. Remove clinic and prescriber identifiers.
3. Replace dates with coarse or synthetic dates.
4. Remove barcodes, QR codes, and prescription IDs.
5. Store files only inside `data/private/`.
6. Confirm `data/private/` contents are ignored by git.
7. Do not upload real data to external AI APIs without formal approval and privacy review.

Future knowledge-base ingestion must preserve source provenance and reviewer metadata, but that provenance must describe reference sources, not patient-specific records.

## Phase 2A OCR Intake

The OCR intake foundation is privacy-safe by default:

- Uploaded images are read in memory and are not stored by default.
- Supported uploads are limited to PNG, JPG, JPEG, and WEBP.
- The mock OCR provider does not call external services.
- OCR output is unverified and must be corrected by a pharmacist before analysis.
- Possible identifier patterns are flagged as warnings, not treated as confirmed patient facts.
- Real prescription images must not be committed to the repository.

If future OCR experiments require local files, they must stay inside `data/private/` or another ignored upload folder and must not be used in commits, tests, or demos.

## Phase 2B OCR Evaluation And Audit

`data/evaluation/ocr_eval_cases.json` contains synthetic OCR text cases only. It must not be replaced with real prescription text or image-derived patient data.

Correction audit metadata is returned directly from `/ocr/confirm-text` and is not persisted in a database in Phase 2B. The audit can include the original OCR text and pharmacist-corrected text, so it must be treated as sensitive workflow data if real records are ever introduced under a future approved process.

Possible identifier findings remain category-level warnings, such as `patient_name_label` or `phone_number_like`. They are not confirmed PII determinations.

## Phase 2C Synthetic OCR Fixtures

`data/evaluation/ocr_fixtures/` contains synthetic PNG files for OCR provider-interface testing. These files must remain synthetic and must not be replaced with real prescription images.

The current OCR providers expose safety metadata for whether a provider is external, stores images, or requires network access. Current providers are local, non-networked, and non-storing. Future providers that use networks or storage require explicit privacy review before being enabled.

## TODO

- Define a formal anonymization checklist.
- Add automated PHI scanning before commits.
- Add a secure local-only upload folder for future OCR experiments.
- Define retention and access rules before any OCR audit persistence is added.
