# Synthetic OCR Fixtures

This directory contains approved synthetic OCR fixture files for Phase 2C provider-interface testing.

Rules:

- Do not add real prescription images.
- Do not add real patient names, phone numbers, IDs, addresses, clinic names, or prescriber data.
- Fixture text, labels, and filenames must be synthetic.
- Identifier-like labels are allowed only when clearly fake and used to test privacy warnings.
- These files are for engineering evaluation only and are not clinical validation.

Current fixture files:

- `synthetic_paracetamol_clean.png`
- `synthetic_ibuprofen_noisy.png`
- `synthetic_amoxicillin_possible_identifier.png`
- `synthetic_no_medication.png`

The Phase 2C `SyntheticFixtureOcrProvider` is filename-driven. The PNG files exist to exercise upload and fixture plumbing without introducing a production OCR engine.
