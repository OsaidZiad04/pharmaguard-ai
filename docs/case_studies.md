# Synthetic Case Studies

The final demo cases live in `data/evaluation/final_demo_cases.json`. They are synthetic and designed for storytelling, not clinical validation.

## Case 1: Clean Single Medication

Shows the happy path: supported medication extraction, local RAG retrieval, governance metadata, and draft-only counseling support.

Expected proof point: source-backed context appears, but patient-facing output remains disabled.

## Case 2: OCR Correction Boundary

Shows that OCR text is unverified and corrected text is the only downstream boundary.

Expected proof point: raw OCR does not automatically trigger prescription analysis or RAG.

## Case 3: Missing Dose Or Frequency

Shows deterministic safety-rule prompts for missing prescription fields.

Expected proof point: the system asks for pharmacist verification instead of inventing details.

## Case 4: Multiple Medications

Shows multiple supported medication extraction and separate source grounding.

Expected proof point: interaction checking is explicitly unavailable and must use validated references.

## Case 5: Unsupported Medication

Shows insufficient context behavior.

Expected proof point: unsupported medication-like text does not retrieve arbitrary local profiles.

## Case 6: Possible Identifier Warning

Shows privacy-aware warning behavior with fake synthetic identifier-like labels.

Expected proof point: possible identifiers are flagged as possible identifiers, not confirmed PII.

## Case 7: Insufficient KB Context

Shows that ambiguous or condition-like text does not infer treatment.

Expected proof point: the system asks for confirmed medication and pharmacist review.
