# Presentation Outline

This outline is for a final portfolio walkthrough. It should not be presented as a clinical validation deck or production medical-device claim.

## 1. Title

- PharmaGuard AI
- Pharmacist-centered prescription support prototype
- Safety-first, synthetic-data-only, evaluation-driven

## 2. Problem

- Pharmacists handle incomplete prescription text, missing context, and counseling preparation under time pressure.
- Generic AI chat flows can blur responsibility and make unsupported medical output look authoritative.
- The core product problem is workflow control, not replacing pharmacist judgment.

## 3. Why Pharmacists Need AI Support

- Help organize prescription text.
- Surface missing fields and review prompts.
- Retrieve source-grounded medication context.
- Keep the pharmacist as the final reviewer.

## 4. Solution Overview

- OCR intake for prescription images.
- Pharmacist correction gate.
- Medication extraction and local RAG retrieval.
- KB governance and retrieval diagnostics.
- Safety-rule prompts and draft counseling support.

## 5. System Architecture

- FastAPI backend.
- Next.js pharmacist dashboard.
- Local Markdown drug profiles.
- In-memory TF-IDF retrieval.
- OCR provider interface with mock/synthetic default providers.
- Synthetic evaluation and reporting scripts.

## 6. OCR Intake And Correction Gate

- OCR output is unverified.
- Uploaded images are not stored by default.
- Tesseract is optional, disabled by default, and benchmark-only unless explicitly policy-enabled.
- Corrected text is the only downstream boundary.

## 7. RAG And Grounded Answers

- Local Markdown profiles are chunked and retrieved with source metadata.
- Unknown or weak-context medications return insufficient context.
- Generated text remains pharmacist-support draft-only.

## 8. KB Governance

- Drug registry tracks review/source/clinical-validation status.
- Current profiles are draft placeholder educational content.
- Patient-facing output is disabled.
- Pharmacist review is mandatory.

## 9. Retrieval Intelligence

- Query classification is deterministic.
- Retrieval diagnostics identify weak, insufficient, placeholder-only, and draft/unvalidated retrieval.
- Strategy comparison keeps the existing default retriever stable.

## 10. Medication Safety Rules

- Deterministic prompts identify missing dose/frequency/duration/route, no medication, unsupported medication text, possible identifiers, and governance risks.
- Interaction and contraindication checking are explicitly unavailable.
- Findings are review prompts, not clinical decisions.

## 11. Evaluation Evidence

- RAG evaluation: 46/46 synthetic cases.
- OCR evaluation: 18/18 synthetic cases.
- E2E workflow evaluation: 10/10 synthetic cases.
- KB governance, safety rules, provider policy, and trace reports pass.
- Results are engineering validation only, not clinical validation.

## 12. Demo Scenario

- Start with a synthetic prescription.
- Show OCR/correction boundary.
- Run analysis and source retrieval.
- Show safety prompts, KB governance, and draft counseling.
- Demonstrate unsupported-medication insufficient context.

## 13. Limitations

- No real patient data.
- No production OCR default.
- No trusted clinical source ingestion.
- No clinical validation.
- No patient-facing final advice.
- No production auth, deployment hardening, or audit database.

## 14. Future Work

- Trusted-source ingestion prototype.
- Pharmacist review and sign-off workflow.
- Drug knowledge graph experiments.
- Production privacy, auth, audit, and deployment planning.

## 15. Closing

- PharmaGuard AI demonstrates safe healthcare AI architecture: boundaries first, evaluation throughout, and pharmacist control preserved.
