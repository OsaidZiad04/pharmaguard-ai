# PharmaGuard AI Final Project Report

## Executive Summary

PharmaGuard AI is a pharmacist-centered AI copilot prototype for prescription intake, pharmacist correction, local RAG retrieval, knowledge-base governance, safety-rule prompts, and evaluation-driven workflow review.

It is not a medical device, not clinically validated, and not a patient-facing advisor. It demonstrates how a safety-first pharmacy AI workflow can be structured so the pharmacist remains in control.

## Problem

Pharmacists often need to interpret incomplete prescription text, check missing context, retrieve medication information, and prepare counseling notes under time pressure. A generic chatbot pattern is unsafe for this setting because it can blur the line between draft support and final clinical judgment.

## Solution

PharmaGuard AI separates workflow stages:

1. Prescription text or synthetic image intake.
2. OCR extraction marked unverified.
3. Pharmacist correction boundary.
4. Prescription analysis and medication extraction.
5. Local Markdown RAG retrieval.
6. Source grounding, governance checks, and retrieval diagnostics.
7. Deterministic medication safety-rule findings.
8. Draft counseling support only after pharmacist confirmation.

## Architecture

The backend uses FastAPI. The frontend is a Next.js pharmacist dashboard. Data is local and synthetic. RAG uses Markdown drug profiles, TF-IDF, an in-memory index, and deterministic grounded generation.

The knowledge base is governed through `drug_registry.json` and `source_catalog.json`. All current profiles remain draft placeholder educational content and not clinically validated.

The frontend uses the PharmaGuard AI brand assets from `frontend/public/brand/` to present a premium pharmacist command-center interface. The visual polish improves screenshot readiness, responsive hierarchy, and future bilingual layout readiness without changing backend behavior.

## Safety Controls

- Pharmacist review is always required.
- Patient-facing output is disabled.
- Unknown medications return insufficient context.
- OCR output is unverified and cannot bypass correction.
- Retrieval diagnostics expose weak or unvalidated context.
- Safety rules prompt missing fields and governance risks.
- Interaction and contraindication checks are explicitly unavailable.

## Evaluation Results

Latest known results:

- Backend tests: 177 passed, 1 skipped.
- RAG evaluation: 46/46 passed.
- Retrieval strategy evaluation: PASS; `existing_default` remains recommended.
- OCR evaluation: 18/18 passed.
- E2E workflow evaluation: 10/10 passed.
- KB governance report: PASS, 0 blockers.
- Safety rules report: PASS, 10/10 synthetic scenarios.
- Trace report: PASS, unverified OCR downstream use blocked in 10/10 traces.

These are engineering checks using synthetic data. They are not clinical validation.

## Limitations

- No real patient data.
- No production OCR.
- Tesseract is optional and disabled by default.
- No external medical APIs.
- No real interaction or contraindication engine.
- No trusted clinical source ingestion.
- No clinical validation.
- No production authentication, authorization, or audit database.

## Future Work

- Capture final screenshots and demo recording using synthetic cases only.
- Add final screenshot set for the branded dashboard and `/evaluation` page.
- Trusted-source ingestion prototype after governance approval.
- Pharmacist review workflow persistence.
- Drug knowledge graph experiments.
- Production deployment hardening only after privacy and validation planning.
