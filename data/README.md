# Data

This directory contains synthetic examples, draft medication knowledge, registry metadata, and evaluation data for development.

## Critical Warning

- Do not commit real prescriptions.
- Do not commit patient names, phone numbers, IDs, addresses, or clinic identifiers.
- Keep real/anonymized test images inside `data/private/`, which is gitignored.

## Contents

- `drug_profiles/`: neutral placeholder Markdown profiles and `drug_registry.json`.
- `sample_prescriptions/`: synthetic prescription text cases only.
- `evaluation/`: synthetic RAG evaluation cases and templates.
- `private/`: local-only storage for files that must not be committed.

Phase 2A OCR intake does not store uploaded images by default. Any future local OCR experiment files must remain in `data/private/` or another gitignored upload directory and must not contain real patient information.

## Current Local Drug Profiles

- paracetamol
- ibuprofen
- amoxicillin
- cetirizine
- loratadine
- omeprazole
- salbutamol
- metformin
- amlodipine
- levothyroxine
- azithromycin
- simvastatin
- diclofenac
- esomeprazole
- aspirin

The profiles are local educational placeholders for pharmacist-support retrieval tests. They are not complete real pharmacy coverage, clinical validation, final medication references, or patient-specific instructions.

`drug_profiles/drug_registry.json` is the governed MVP registry for this folder. It tracks supported generic names, conservative aliases, profile files, draft review status, placeholder source status, safety notes, and whether a profile is enabled for local RAG. All current entries are draft and unreviewed.

Adding hundreds of manual Markdown files is not the intended long-term strategy. Future scale should use structured ingestion with provenance, source versioning, validation, and pharmacist approval before a profile is enabled.

## TODO

- Add automated checks that reject likely patient identifiers.
- Add reviewed source metadata when approved reference documents are introduced.
