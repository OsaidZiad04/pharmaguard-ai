# Data

This directory contains synthetic examples and placeholder medication knowledge for development.

## Critical Warning

- Do not commit real prescriptions.
- Do not commit patient names, phone numbers, IDs, addresses, or clinic identifiers.
- Keep real/anonymized test images inside `data/private/`, which is gitignored.

## Contents

- `drug_profiles/`: neutral placeholder Markdown profiles.
- `sample_prescriptions/`: synthetic prescription text cases only.
- `evaluation/`: synthetic RAG evaluation cases and templates.
- `private/`: local-only storage for files that must not be committed.

## Current Local Drug Profiles

- paracetamol
- ibuprofen
- amoxicillin
- cetirizine
- loratadine
- omeprazole
- salbutamol

The profiles are local educational placeholders for pharmacist-support retrieval tests. They are not clinical validation, final medication references, or patient-specific instructions.

## TODO

- Add automated checks that reject likely patient identifiers.
- Add source metadata when real approved reference documents are introduced.
