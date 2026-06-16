# Synthetic OCR Fixtures

This directory contains approved synthetic OCR fixture files for Phase 2C provider-interface testing.

Rules:

- Do not add real prescription images.
- Do not add real patient names, phone numbers, IDs, addresses, clinic names, or prescriber data.
- Fixture text, labels, and filenames must be synthetic.
- Identifier-like labels are allowed only when clearly fake and used to test privacy warnings.
- These files are for engineering evaluation only and are not clinical validation.

Current PNG fixture files:

- `synthetic_paracetamol_clean.png`
- `synthetic_ibuprofen_noisy.png`
- `synthetic_amoxicillin_possible_identifier.png`
- `synthetic_no_medication.png`

Current descriptor fixtures:

- `synthetic_metformin_clean.fixture.md`
- `synthetic_amlodipine_low_contrast.fixture.md`
- `synthetic_azithromycin_spaced_text.fixture.md`
- `synthetic_multiple_meds.fixture.md`
- `synthetic_identifier_heavy_fake.fixture.md`
- `synthetic_handwriting_like_noise.fixture.md`

The `SyntheticFixtureOcrProvider` is filename-driven. PNG files and descriptor fixtures exist to exercise upload/evaluation plumbing without introducing a production OCR engine.

Phase 2J uses only real synthetic image fixtures for the optional Tesseract benchmark. Descriptor fixtures are skipped by that benchmark and remain filename-driven cases for the synthetic fixture provider.
