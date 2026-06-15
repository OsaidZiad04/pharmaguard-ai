# PharmaGuard AI — Project State

This is the living single source of truth for the current PharmaGuard AI project state. It must be updated after every future implementation phase before handoff.

## 1. Project Vision

PharmaGuard AI is a pharmacist-centered prescription support system being built incrementally toward real pharmacy workflow readiness. The project is not a final medical product and does not claim clinical validation. Each phase should strengthen the system architecture, safety controls, evaluation coverage, privacy posture, and pharmacist workflow while remaining realistic and testable.

The system is designed around these principles:

- Pharmacists stay in control.
- Outputs remain draft-only support.
- OCR and extraction are assistive signals, not final truth.
- Unknown or weak-context cases must not be guessed.
- Real patient data must not be used in this repository.
- Future production readiness requires validation, governance, privacy controls, and pharmacist review.

## 2. Current System Summary

The current system includes:

- FastAPI backend.
- Next.js + TypeScript + Tailwind pharmacist dashboard.
- Local RAG over Markdown drug profiles.
- Structured drug registry and knowledge-base validation.
- Privacy-safe OCR intake foundation using a deterministic local mock OCR provider.
- Pharmacist OCR correction workflow.
- OCR correction audit metadata returned by `/ocr/confirm-text`.
- RAG evaluation with synthetic cases.
- OCR evaluation with synthetic cases.
- Knowledge-base coverage report.
- Safety guardrails for low confidence, missing patient context, unknown medications, and insufficient local context.

The current system does not include:

- Real patient data.
- External OCR APIs.
- External medical APIs.
- Dense retrieval.
- Production OCR.
- Clinical validation claims.
- Persistent audit database.
- Final medical advice.

## 3. Current Architecture

Current workflow:

`Prescription text input OR prescription image upload -> OCR extraction if image is used -> OCR output marked unverified -> pharmacist correction -> corrected text can be sent to prescription analysis -> medication extraction -> RAG retrieval from local drug knowledge base -> grounded drug information / counseling draft -> pharmacist final review`

### RAG Pipeline

The local RAG pipeline loads Markdown drug profiles from `data/drug_profiles/`, chunks them by headings and paragraphs, embeds chunks with local TF-IDF, stores them in an in-memory vector index, retrieves medication-specific context, validates citations, and generates grounded pharmacist-support drafts. If relevant context is missing or weak, the system returns insufficient knowledge-base context instead of guessing.

### KB Registry Pipeline

The knowledge base is governed by `data/drug_profiles/drug_registry.json`. The registry tracks generic names, aliases, profile files, review status, source status, safety notes, and whether a profile is enabled for RAG. The KB validator checks required registry fields, required Markdown sections, missing files, alias conflicts, disabled profiles, and unreviewed draft profiles. The KB report summarizes coverage and validation status.

### OCR Pipeline

The OCR intake pipeline accepts supported synthetic image uploads, reads them in memory, runs a deterministic local `MockOcrProvider`, returns unverified OCR text, flags possible identifier patterns, and requires pharmacist correction. `/ocr/confirm-text` returns corrected text and correction audit metadata. OCR output does not automatically trigger prescription analysis, RAG, lookup, or counseling.

### Frontend Workflow

The frontend is a pharmacist dashboard, not a chatbot. It includes prescription image intake, editable OCR correction, prescription text analysis, pharmacist review, drug information, knowledge-base context, safety alerts, and counseling draft display. Corrected OCR text only enters the prescription text flow after an explicit pharmacist action.

## 4. Completed Phases

### Phase 0: Scaffolding

- Objective: Establish the initial repository structure and working app foundation.
- Main files/modules added: `backend/`, `frontend/`, `data/`, `docs/`, FastAPI app, Next.js app, initial tests, `.env.example` files.
- Key behavior added: Health endpoint, placeholder prescription analysis, drug lookup, counseling routes, dashboard shell, synthetic sample data, safety and privacy docs.
- Verification summary: Initial backend and frontend scaffold ran with placeholder logic.

### Phase 1: Local RAG MVP

- Objective: Replace basic mock lookup with local retrieval over Markdown drug profiles.
- Main files/modules added: `backend/app/rag/chunker.py`, `embedder.py`, `vector_store.py`, `retriever.py`, `generator.py`, `prompt_templates.py`, `backend/app/api/routes_rag.py`.
- Key behavior added: Markdown chunking, TF-IDF embedding, in-memory retrieval, grounded draft generation, `/rag/query`, RAG-backed drug lookup and counseling.
- Verification summary: RAG endpoint returned relevant chunks for supported drugs and insufficient context for unknown medication names.

### Phase 1.5: RAG Hardening & Evaluation

- Objective: Add regression evaluation, citation validation, and unsupported-claim protection.
- Main files/modules added: `data/evaluation/rag_eval_cases.json`, `backend/app/rag/evaluation.py`, `backend/app/rag/citation_validator.py`, `backend/scripts/evaluate_rag.py`, RAG safety tests.
- Key behavior added: Synthetic RAG evaluation runner, citation validation, forbidden language checks, unsupported-information checks, draft/pharmacist-review framing checks.
- Verification summary: RAG evaluation passes 46/46 cases in the current project state.

### Phase 1.6: Knowledge Base & Evaluation Expansion

- Objective: Expand local drug coverage and synthetic evaluation coverage.
- Main files/modules added: Additional Markdown drug profiles and expanded RAG evaluation cases.
- Key behavior added: More supported medications, conservative alias coverage, condition-only query safeguards, exact-dose/final-advice regression cases.
- Verification summary: Expanded synthetic RAG evaluation remained passing.

### Phase 1.7: Controlled Knowledge Base Expansion

- Objective: Increase MVP drug coverage while keeping safety-first constraints.
- Main files/modules added: Additional Markdown profiles for metformin, amlodipine, levothyroxine, azithromycin, simvastatin, diclofenac, esomeprazole, and aspirin.
- Key behavior added: Local knowledge base expanded to 15 profiles, conservative aliases added, extraction coverage updated, condition-only queries still avoid arbitrary medication mapping.
- Verification summary: RAG evaluation passed with 46 synthetic cases.

### Phase 1.8: Scalable Drug Knowledge Base Architecture

- Objective: Move from loose Markdown profiles toward a governed, scalable knowledge-base architecture.
- Main files/modules added: `data/drug_profiles/drug_registry.json`, `backend/app/kb/`, `backend/scripts/kb_report.py`, `docs/kb_scaling_plan.md`.
- Key behavior added: Registry loading, generic and alias lookup, enabled-profile listing, profile validation, alias conflict detection, KB coverage reporting, future ingestion stubs.
- Verification summary: KB report passes with 15 draft profiles, 0 blocking issues, and expected draft-profile warnings.

### Phase 2A: Privacy-Safe OCR Intake Foundation

- Objective: Add a safe OCR intake boundary without production OCR.
- Main files/modules added: `backend/app/schemas/ocr.py`, `backend/app/api/routes_ocr.py`, `backend/app/services/ocr_service.py`, `frontend/components/PrescriptionImageUploadCard.tsx`.
- Key behavior added: `/ocr/extract-image`, supported image validation, upload size guard, deterministic mock OCR provider, possible identifier warnings, `/ocr/confirm-text`, frontend correction workflow.
- Verification summary: OCR upload and confirm-text tests pass; images are not stored by default; OCR output cannot bypass pharmacist correction.

### Phase 2B: OCR Evaluation & Pharmacist Correction Audit

- Objective: Add synthetic OCR evaluation and returned correction audit metadata around OCR intake.
- Main files/modules added: `data/evaluation/ocr_eval_cases.json`, `backend/app/ocr/evaluation.py`, `backend/app/services/ocr_audit_service.py`, `backend/scripts/evaluate_ocr.py`, `docs/ocr_evaluation.md`.
- Key behavior added: Character error rate, word error rate, token overlap, medication term hit checks, privacy warning matching, correction audit metadata from `/ocr/confirm-text`, frontend audit summary.
- Verification summary: OCR evaluation passes 10/10 synthetic cases; backend tests pass 54 tests.

## 5. Supported Knowledge Base

Current total drug profiles: 15.

Current supported medications:

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

Registry file: `data/drug_profiles/drug_registry.json`.

Current registry status:

- `review_status`: `draft`
- `source_status`: `placeholder_educational`
- All profiles are draft educational placeholder content.
- No profile is clinically validated.
- The current KB is suitable for local workflow and evaluation scaffolding only.

## 6. Evaluation Status

Current verification status:

- Backend tests: 54 passed.
- RAG evaluation: 46/46 passed.
- OCR evaluation: 10/10 passed.
- KB report: PASS, 0 blocking issues.
- Frontend typecheck: passed.
- Frontend build: passed.

Verification commands:

```bash
cd backend && python -m pytest
cd backend && python scripts/evaluate_rag.py
cd backend && python scripts/kb_report.py
cd backend && python scripts/evaluate_ocr.py
cd frontend && npm run typecheck
cd frontend && npm run build
```

## 7. Safety and Privacy Boundaries

Current non-negotiable boundaries:

- Pharmacist review is required.
- Outputs are draft-only.
- The system must not provide final medical advice.
- Unknown medications must not be guessed.
- Weak or missing local context returns insufficient knowledge-base context.
- No real patient data belongs in the repository.
- Uploaded images are not stored by default.
- OCR output is unverified.
- OCR text must be corrected or confirmed by a pharmacist before analysis.
- Possible identifiers are flagged as possible identifiers, not confirmed PII.
- No external APIs are used.
- No clinical validation is claimed.

## 8. Important Files and Directories

- `backend/app/main.py`: FastAPI application factory and route wiring.
- `backend/app/api/`: HTTP route modules for health, prescriptions, drugs, counseling, RAG, and OCR.
- `backend/app/services/`: Application services for extraction, safety, lookup, counseling, RAG orchestration, OCR, and OCR audit.
- `backend/app/rag/`: Local TF-IDF RAG components, generation, citation validation, and RAG evaluation.
- `backend/app/kb/`: Drug registry loading, KB validation, coverage schema, and future ingestion scaffolding.
- `backend/app/ocr/`: OCR evaluation metrics and synthetic OCR evaluation runner logic.
- `backend/scripts/`: CLI scripts for RAG evaluation, KB reporting, and OCR evaluation.
- `backend/tests/`: Backend pytest regression tests.
- `frontend/components/`: Pharmacist dashboard UI components.
- `frontend/lib/`: Frontend API client and shared TypeScript types.
- `data/drug_profiles/`: Draft educational Markdown profiles and drug registry.
- `data/evaluation/`: Synthetic RAG and OCR evaluation datasets.
- `docs/`: Architecture, safety, privacy, roadmap, OCR evaluation, KB scaling, and living project documentation.

## 9. Current Limitations

- OCR is mock-only.
- No real OCR provider is integrated.
- No real prescription images are used.
- No persistent audit database exists.
- Retrieval uses local TF-IDF only.
- The knowledge base is draft educational placeholder content only.
- There is no clinical validation.
- Deployment is not hardened.
- Production authentication and authorization are not implemented.
- Real pharmacy system integration is not implemented.
- Audit retention, access controls, and review sign-off workflows are not production-ready.

## 10. Recommended Next Phases

Proposed roadmap:

- Phase 2C: OCR Provider Interface & Synthetic Image Fixtures.
- Phase 2D: OCR Quality Benchmarking and Provider Swap Readiness.
- Phase 3: End-to-End Prescription Workflow Evaluation.
- Phase 4: Drug Knowledge Graph.
- Phase 5: Deployment & Portfolio Polish.
- Future: pharmacist review workflow, authentication, real validated sources, production database, audit persistence, retention policy, access control, and pharmacy-system integration.

## 11. Living Documentation Rule

Every future Codex phase must update this file before handoff.

Future handoffs should include:

- Phase name.
- Files created.
- Files modified.
- Tests run.
- Evaluation results.
- Safety/privacy impact.
- Remaining limitations.
- Recommended next step.
