# Safety Protocol

PharmaGuard AI supports pharmacists only. It does not replace professional judgment, clinical guidelines, legal requirements, or local pharmacy policy.

## Non-Negotiable Guardrails

- Never present AI output as a final medical decision.
- Treat OCR text as unverified until pharmacist correction.
- Require pharmacist confirmation before generating patient-facing counseling drafts.
- Treat low confidence extraction as review-required.
- Do not guess unknown medication names.
- Warn when patient context is missing:
  - age
  - pregnancy status
  - allergies
  - current medications

## Current Scaffold Behavior

The backend safety service always sets pharmacist review as required. The UI displays draft-only wording and separates extraction, drug information, safety alerts, and counseling note output.

Phase 2A adds OCR intake as an assistive input layer. `/ocr/extract-image` returns unverified mock OCR text and possible privacy warnings. `/ocr/confirm-text` records pharmacist-corrected text as eligible for prescription analysis, but it does not automatically invoke analysis, RAG, counseling, or drug lookup.

Phase 2B adds synthetic OCR evaluation metrics and returned correction audit metadata. Character error rate, word error rate, token overlap, medication term hits, and privacy-warning matches are engineering checks only. They do not validate clinical correctness, patient identity, diagnosis, treatment, or production OCR quality.

Phase 2C adds explicit OCR provider safety metadata. Current providers are local, non-external, non-networked, and non-storing. Explicit external provider names are rejected in prototype mode. Provider metadata must not be used to bypass pharmacist correction or downstream safety checks.

Phase 2G adds end-to-end synthetic workflow evaluation. It verifies that unverified OCR output is not sent downstream, corrected text is the boundary for prescription analysis, supported medications retrieve source-grounded RAG context, and counseling drafts remain pharmacist-support only. This evaluation is an engineering check, not clinical validation.

Phase 2H adds workflow traceability for synthetic E2E cases. Traces explicitly record that unverified OCR downstream use is blocked, pharmacist correction is required, corrected text is used for downstream analysis, RAG sources are checked, counseling remains draft-only, and pharmacist review remains required. Traces do not store raw image bytes or real patient data.

Phase 2I makes these safety boundaries more visible in the pharmacist dashboard. The UI shows OCR as unverified, correction as required before analysis, source grounding status, draft-only counseling status, and pharmacist review required. This is visual workflow support only and does not change backend safety behavior.

Phase 2L-M adds controlled OCR activation policy. Tesseract remains blocked in default workflow and production. It can be benchmarked only through benchmark scripts, and it can enter explicit prototype workflow mode only when local dependencies, explicit enablement, and recorded benchmark gates pass. Even then, OCR output remains unverified, image storage remains disabled, and pharmacist correction remains mandatory.

Phase 3A adds knowledge-base governance metadata. Current drug profiles remain draft educational placeholders, not clinically validated sources. `patient_facing_allowed` is false for every current profile, `requires_pharmacist_review` is true, and counseling output remains draft-only under pharmacist review. The governance report is an engineering safety check, not clinical validation.

Phase 3B-C adds retrieval diagnostics, deterministic query classification, and medication safety-rule findings. These findings are pharmacist-review prompts only. They do not validate drug-drug interactions, contraindications, diagnosis, treatment choice, patient-specific dosing, or prescription appropriateness.

## Unsafe Output Avoidance

The system should avoid:

- final dosing recommendations
- diagnosis
- treatment selection
- drug substitution decisions
- claims that a medication is appropriate for a specific patient
- claims that draft placeholder KB content is clinically validated
- hidden assumptions about allergies, pregnancy, age, renal function, or drug interactions
- claims that retrieval diagnostics or safety rules prove a prescription is safe or appropriate

## Human Control

The pharmacist must verify:

- prescription text accuracy
- OCR correction accuracy before analysis
- medication identity
- dose, route, frequency, and duration
- patient-specific risk factors
- counseling note correctness
- retrieved source governance status and whether profile content is draft or validated
- deterministic safety-rule findings and their limitations
- whether the output is appropriate to share

## TODO

- Add source citations for every RAG-supported statement.
- Add structured pharmacist sign-off metadata.
- Add evaluation checks for unsafe claims.
- Add logging that excludes protected health information.
- Add synthetic image fixtures before any production OCR provider is considered.
- Expand synthetic fixture coverage before any production OCR provider is considered.
- Add pharmacist sign-off and audit-retention policy before correction audits are stored.
- Add validated source ingestion before any real interaction or contraindication checking.
