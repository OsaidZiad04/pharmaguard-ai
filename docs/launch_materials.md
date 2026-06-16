# Launch Materials

These drafts are for portfolio sharing. They must not imply clinical validation, medical-device status, production readiness, or patient-facing advice.

## LinkedIn Post Draft

I built PharmaGuard AI, a pharmacist-centered AI copilot prototype for prescription workflow support.

The project focuses on safety boundaries rather than autonomous medical advice:

- OCR output is unverified.
- Pharmacist correction is required before analysis.
- Local RAG retrieves source-grounded medication context from governed draft profiles.
- Safety rules produce pharmacist-review prompts, not clinical decisions.
- Evaluation scripts cover RAG, OCR, E2E workflow, KB governance, provider policy, traceability, and safety rules.

This is a prototype using synthetic data and draft educational placeholder content only. It is not clinical validation and not a patient-facing medical advisor.

What I wanted to show: how healthcare AI can be designed around pharmacist control, privacy boundaries, source governance, and regression evaluation from the start.

## GitHub Project Description

Pharmacist-centered AI copilot prototype with privacy-safe OCR intake, correction-gated workflow, local RAG, KB governance, retrieval diagnostics, medication safety-rule prompts, traceability, and synthetic evaluation.

## Short Project Pitch

PharmaGuard AI is a safety-first pharmacist dashboard prototype. It demonstrates OCR intake, pharmacist correction, local source-grounded RAG, knowledge-base governance, deterministic safety prompts, and synthetic evaluation without real patient data or final medical advice.

## 30-Second Pitch

PharmaGuard AI is a pharmacist-centered AI copilot prototype. The key design choice is that OCR and AI outputs never become final truth: OCR is unverified, pharmacist correction is required, RAG answers are source-grounded, and counseling stays draft-only. The project includes governance metadata, safety rules, traceability, and evaluation reports using synthetic data only.

## 60-Second Pitch

PharmaGuard AI is a full-stack healthcare AI portfolio project built around safety and workflow control. The backend uses FastAPI, local Markdown drug profiles, TF-IDF RAG, KB governance, OCR provider policy, retrieval diagnostics, and deterministic medication safety rules. The frontend is a Next.js pharmacist dashboard that shows OCR correction, source grounding, safety prompts, and pharmacist review requirements. The project includes synthetic RAG, OCR, E2E, traceability, provider, governance, and safety evaluations. It is a prototype only: no real patient data, no clinical validation claim, no patient-facing final advice, and pharmacist review is mandatory.

## Technical Interview Explanation

The hardest part was not adding RAG or OCR in isolation. The hard part was defining safe interfaces between workflow stages:

- OCR is an assistive input, not verified prescription text.
- Corrected text is the boundary before analysis.
- Retrieval must return insufficient context instead of guessing.
- KB governance must expose draft/unvalidated source status.
- Safety rules must be deterministic review prompts, not clinical decision rules.
- Evaluation scripts must prove these boundaries keep working.

## What Makes This Project Strong

- It treats healthcare AI as a workflow and governance problem, not a chatbot problem.
- It has clear safety boundaries and honest limitations.
- It is testable locally without external APIs.
- It uses synthetic data only.
- It includes backend, frontend, data, documentation, reports, and final demo material.
- It preserves pharmacist authority and avoids final medical advice.
