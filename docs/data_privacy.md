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

## Real Prescription Handling

If real prescriptions are ever used for local experimentation:

1. Remove direct identifiers.
2. Remove clinic and prescriber identifiers.
3. Replace dates with coarse or synthetic dates.
4. Remove barcodes, QR codes, and prescription IDs.
5. Store files only inside `data/private/`.
6. Confirm `data/private/` contents are ignored by git.
7. Do not upload real data to external AI APIs without formal approval and privacy review.

## TODO

- Define a formal anonymization checklist.
- Add automated PHI scanning before commits.
- Add a secure local-only upload folder for future OCR experiments.
