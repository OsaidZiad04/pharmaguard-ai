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
- Privacy-safe OCR intake foundation using deterministic local OCR providers.
- OCR provider interface with safe provider metadata.
- Synthetic OCR fixture provider and fixture-backed OCR evaluation.
- OCR provider quality gates and provider-level benchmark summaries.
- OCR provider candidate registry and swap-readiness matrix.
- Disabled-by-default Tesseract local OCR adapter, dependency checks, and optional synthetic benchmark path.
- OCR-readable synthetic PNG fixtures with fixture inspection.
- Controlled OCR activation policy with safe defaults and policy reporting.
- Knowledge-base governance metadata, source catalog, and governance reporting.
- Retrieval strategy comparison, retrieval diagnostics, and query classification.
- Deterministic medication safety-rule findings for pharmacist workflow support.
- End-to-end OCR-to-RAG workflow evaluation.
- Workflow traceability and pharmacist review audit records for synthetic E2E cases.
- Pharmacist dashboard workflow polish with visible status and safety panels.
- Optional local Tesseract OCR benchmarking against synthetic fixtures only.
- Safe explicit Tesseract prototype workflow mode behind policy gates.
- Pharmacist OCR correction workflow.
- OCR correction audit metadata returned by `/ocr/confirm-text`.
- RAG evaluation with synthetic cases.
- OCR evaluation with synthetic cases.
- End-to-end OCR-to-RAG workflow evaluation with synthetic cases.
- Deterministic synthetic workflow trace export and trace report.
- OCR provider readiness report.
- Knowledge-base coverage report.
- Knowledge-base governance report.
- Retrieval strategy evaluation report.
- Medication safety rules report.
- Safety guardrails for low confidence, missing patient context, unknown medications, and insufficient local context.

The current system does not include:

- Real patient data.
- External OCR APIs.
- External medical APIs.
- Dense retrieval.
- Real clinical interaction or contraindication checking.
- Production OCR.
- Default Tesseract, EasyOCR, or cloud OCR provider integration.
- Clinical validation claims.
- Persistent audit database.
- Final medical advice.

## 3. Current Architecture

Current workflow:

`Prescription text input OR prescription image upload -> OCR extraction if image is used -> OCR output marked unverified -> pharmacist correction -> corrected text can be sent to prescription analysis -> medication extraction -> RAG retrieval from local drug knowledge base -> grounded drug information / counseling draft -> pharmacist final review`

### RAG Pipeline

The local RAG pipeline loads Markdown drug profiles from `data/drug_profiles/`, chunks them by headings and paragraphs, embeds chunks with local TF-IDF, stores them in an in-memory vector index, retrieves medication-specific context, validates citations, and generates grounded pharmacist-support drafts. If relevant context is missing or weak, the system returns insufficient knowledge-base context instead of guessing. Phase 3B adds diagnostic retrieval strategies, query classification, and retrieval-quality reporting around the existing retriever. The default production path remains the current medication-aware TF-IDF retriever.

### Safety Rules Pipeline

Phase 3C adds deterministic medication safety-rule findings to prescription analysis. Rules can flag missing dose/frequency/duration/route, multiple medications, unsupported medication-like text, no medication detected, possible identifiers, placeholder-only KB context, not-clinically-validated profiles, pharmacist review requirements, and patient-facing output blocks. Interaction and contraindication checks are explicitly unavailable and require future trusted-source ingestion. These findings are pharmacist-support prompts only.

### KB Registry Pipeline

The knowledge base is governed by `data/drug_profiles/drug_registry.json`. The registry tracks generic names, aliases, profile files, review status, source status, safety notes, and whether a profile is enabled for RAG. Phase 3A adds governance fields for profile identity, clinical validation status, pharmacist review requirements, patient-facing restrictions, counseling draft allowance, source references, reviewer role, and review timestamps. `data/drug_profiles/source_catalog.json` defines source categories and requirements for future trusted-source ingestion. The KB validator checks required registry fields, required Markdown sections, missing files, alias conflicts, disabled profiles, and unreviewed draft profiles. The KB governance validator checks source/review/clinical-validation metadata and unsafe output policy. The KB reports summarize coverage, validation, and governance status.

### OCR Pipeline

The OCR intake pipeline accepts supported synthetic image uploads, reads them in memory, runs a deterministic local OCR provider, returns unverified OCR text, flags possible identifier patterns, and requires pharmacist correction. `/ocr/confirm-text` returns corrected text and correction audit metadata. OCR output does not automatically trigger prescription analysis, RAG, lookup, or counseling.

Current OCR providers:

- `mock_ocr_phase_2a`
- `synthetic_fixture_phase_2c`

Both current providers are local, non-external, non-networked, and non-storing.

Inactive benchmark-only adapter:

- `tesseract_local_candidate`

The Tesseract adapter is disabled by default and not the default provider. It can run through the explicit synthetic benchmark command when optional local dependencies are available. It can enter `prototype_explicit` workflow mode only when activation policy gates pass. Benchmark results are engineering checks and do not imply production readiness.

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

### Phase 2C: OCR Provider Interface & Synthetic Image Fixtures

- Objective: Prepare the OCR layer for future provider integration while keeping current OCR local, deterministic, privacy-safe, and pharmacist-in-the-loop.
- Main files/modules added: `backend/app/ocr/providers.py`, `backend/scripts/ocr_provider_report.py`, `data/evaluation/ocr_fixtures/`, `docs/ocr_provider_strategy.md`.
- Key behavior added: Provider interface, safe provider selection, explicit external-provider rejection, provider safety metadata in OCR responses, `SyntheticFixtureOcrProvider`, fixture-backed OCR evaluation, and OCR provider readiness reporting.
- Verification summary: Backend tests pass 65 tests; OCR evaluation passes 10/10 cases with 4 fixture-backed cases; OCR provider report lists 2 allowed local providers.

### Phase 2D: OCR Quality Benchmarking & Provider Swap Readiness

- Objective: Strengthen OCR provider evaluation before any real provider integration.
- Main files/modules added: `backend/app/ocr/quality_gates.py`, expanded `data/evaluation/ocr_fixtures/` descriptors, expanded OCR evaluation cases, provider gate tests.
- Key behavior added: OCR evaluation expanded to 18 synthetic cases, 10 fixture-backed cases, provider-level benchmark summaries, quality gate summary, and provider report quality eligibility.
- Verification summary: Backend tests pass 72 tests; OCR evaluation passes 18/18 cases; both current providers pass prototype quality gates.

### Phase 2E: OCR Provider Candidate Comparison & Swap Readiness Matrix

- Objective: Compare future OCR provider candidates without integrating or executing them.
- Main files/modules added: `data/evaluation/ocr_provider_candidates.json`, `backend/app/ocr/provider_candidates.py`, `backend/app/ocr/provider_swap_readiness.py`, `backend/scripts/ocr_candidate_report.py`, `docs/ocr_candidate_comparison.md`.
- Key behavior added: Candidate metadata registry, prototype allowance policy, planned/disallowed candidate summaries, swap-readiness checks, and candidate report.
- Verification summary: Backend tests pass 84 tests; candidate report lists 5 candidates with 2 implemented, 2 planned, and 1 disallowed for prototype mode.

### Phase 2F: Optional Local OCR Provider Adapter Spike

- Objective: Prepare a future local Tesseract OCR integration boundary without installing or activating real OCR.
- Main files/modules added: `backend/app/ocr/local_tesseract_provider.py`, `backend/app/ocr/provider_dependencies.py`, `docs/local_ocr_adapter_plan.md`, provider/dependency tests.
- Key behavior added: `TesseractLocalOcrProvider` behind `BaseOcrProvider`, dependency status checks for `pytesseract` and the local Tesseract binary, explicit prototype-mode rejection when Tesseract is requested, and provider/candidate reports that show the adapter as inactive.
- Verification summary: Backend tests pass 95 tests; provider report lists 2 active local providers and 1 inactive Tesseract adapter; candidate report still lists 5 candidates with cloud OCR blocked.

### Phase 2G: End-to-End OCR-to-RAG Workflow Evaluation

- Objective: Verify the integrated safe workflow from OCR-like input through pharmacist correction, prescription analysis, RAG retrieval, and counseling draft generation.
- Main files/modules added: `data/evaluation/e2e_workflow_cases.json`, `backend/app/workflows/e2e_evaluation.py`, `backend/scripts/evaluate_e2e_workflow.py`, `docs/e2e_workflow_evaluation.md`.
- Key behavior added: Synthetic workflow cases, direct service-level evaluator, corrected-text downstream boundary checks, supported/unsupported medication checks, RAG source grounding checks, counseling availability checks, privacy-warning checks, and pharmacist-review-required checks.
- Verification summary: Backend tests pass 103 tests; E2E workflow evaluation passes 10/10 synthetic cases.

### Phase 2H: Workflow Traceability & Pharmacist Review Audit Records

- Objective: Add structured synthetic workflow trace records for safe pharmacist-in-the-loop explainability and future audit readiness.
- Main files/modules added: `backend/app/workflows/trace.py`, `backend/scripts/export_e2e_traces.py`, `backend/scripts/e2e_trace_report.py`, `data/evaluation/generated/e2e_traces.json`, `docs/workflow_traceability.md`.
- Key behavior added: Trace models, E2E trace generation, deterministic synthetic trace export, trace reporting, correction-boundary trace steps, blocked unverified-OCR downstream step, RAG source refs, safety flags, and pharmacist review records.
- Verification summary: Backend tests pass 113 tests; trace export produces 10 synthetic traces; trace report shows unverified OCR downstream use blocked in all 10 traces.

### Phase 2I: Pharmacist Dashboard Workflow Polish

- Objective: Make the safety-first pharmacist workflow visually clear in the dashboard without changing backend behavior.
- Main files/modules added: `frontend/components/WorkflowStatusPanel.tsx`, `frontend/components/SafetyReviewPanel.tsx`, `frontend/components/SourceGroundingPanel.tsx`, `docs/pharmacist_dashboard_workflow.md`.
- Key behavior added: Ordered workflow status display, OCR correction-boundary messaging, provider/no-storage/local-only OCR indicators, compact safety/review indicators, source-grounding metrics, insufficient-context visibility, and pharmacist review reminders.
- Verification summary: Backend tests pass 113 tests; all existing backend reports pass; frontend typecheck and build pass.

### Phase 2J: Local Tesseract OCR Benchmarking with Synthetic Fixtures Only

- Objective: Benchmark the optional local Tesseract adapter against synthetic image fixtures without making it default or active in the pharmacist workflow.
- Main files/modules added: `backend/app/ocr/tesseract_benchmark.py`, `backend/scripts/benchmark_tesseract_ocr.py`, `docs/tesseract_benchmarking.md`, Tesseract benchmark tests.
- Key behavior added: Runtime-only Pillow/`pytesseract` imports, benchmark-mode-only extraction, descriptor fixture skipping, Tesseract benchmark metrics, quality gate reporting, graceful skipped status when dependencies are unavailable, and provider/candidate report fields for benchmark availability.
- Verification summary: Backend tests pass with the benchmark test skipped when optional local extraction is unavailable. The optional Tesseract benchmark command runs and exits successfully. In the current runtime, `pytesseract` and Pillow are importable, but the local `tesseract` binary is not on `PATH`, so the benchmark reports a skipped status instead of failing normal verification.

### Phase 2K: OCR-Readable Synthetic Fixtures & Tesseract Benchmark Diagnostics

- Objective: Replace invalid tiny PNG OCR fixtures with deterministic, readable synthetic text images and improve benchmark diagnostics.
- Main files/modules added: `backend/scripts/generate_ocr_fixtures.py`, `backend/scripts/inspect_ocr_fixtures.py`, `backend/app/ocr/fixture_inspection.py`, OCR fixture generation tests.
- Key behavior added: Readable synthetic PNG fixtures, fixture inspection for blank/small/low-contrast images, richer Tesseract benchmark diagnostics, preprocessing attempt summaries, and synthetic-only fixture policy documentation.
- Verification summary: Fixture generation and inspection pass; Tesseract benchmark runs against readable synthetic fixtures when dependencies are available and remains optional.

### Phase 2L-M: Controlled Local OCR Activation Policy & Safe Tesseract Workflow Mode

- Objective: Define and enforce OCR provider activation policy while keeping Tesseract disabled by default and correction-gated.
- Main files/modules added: `backend/app/ocr/activation_policy.py`, `backend/app/ocr/ocr_config.py`, `backend/scripts/ocr_activation_policy_report.py`, `docs/ocr_activation_policy.md`, activation policy tests.
- Key behavior added: Safe OCR config defaults, provider/mode policy evaluation, default workflow blocking for Tesseract, benchmark-mode gating, explicit prototype-mode gating, route-level benchmark-mode block, provider/candidate activation reporting, and correction-gate requirements for all providers.
- Verification summary: Activation policy tests pass; reports show mock OCR as default, Tesseract blocked in default workflow and production, cloud OCR blocked, and correction gate required.

### Phase 3A: Knowledge Base Governance Upgrade

- Objective: Upgrade the local drug knowledge base into a review-aware, source-aware governance layer without changing clinical content or claiming validation.
- Main files/modules added: `data/drug_profiles/source_catalog.json`, `backend/app/kb/governance.py`, `backend/scripts/kb_governance_report.py`, `docs/kb_governance.md`, governance tests.
- Key behavior added: Governance metadata for all 15 profiles, source catalog categories, patient-facing output restrictions, counseling draft allowance under pharmacist review, clinical validation status checks, source-reference requirements for trusted-source-ready profiles, governance summary in `kb_report.py`, and governance metadata on retrieved RAG chunks.
- Verification summary: Current profiles remain draft, placeholder educational, not clinically validated, not patient-facing, and pharmacist-review-required; governance report passes with 0 blockers and expected draft/placeholder warnings.

### Phase 3B-C: Retrieval Intelligence & Medication Safety Rules

- Objective: Add retrieval diagnostics, strategy comparison, query/risk classification, and deterministic medication safety-rule prompts without replacing the RAG architecture or creating a clinical decision engine.
- Main files/modules added: `backend/app/rag/retrieval_strategies.py`, `backend/app/rag/retrieval_diagnostics.py`, `backend/app/rag/query_classifier.py`, `backend/app/rag/retrieval_evaluation.py`, `backend/app/safety/medication_rules.py`, `backend/app/safety/safety_models.py`, `backend/scripts/evaluate_retrieval_strategies.py`, `backend/scripts/safety_rules_report.py`, `docs/retrieval_intelligence.md`, `docs/medication_safety_rules.md`, `docs/trusted_source_ingestion_plan.md`, `docs/pharmacist_review_workflow.md`.
- Key behavior added: Existing default retriever comparison against lexical, metadata-boosted, and hybrid-local strategies; retrieval diagnostics returned as additive RAG metadata; deterministic query classification; prescription-analysis safety findings; synthetic safety-rule report; explicit interaction/contraindication-unavailable policy; trusted-source and pharmacist-review workflow design plans.
- Verification summary: Retrieval strategy evaluation keeps `existing_default` as recommended default; safety rules report passes synthetic scenarios; patient-facing output remains disabled and pharmacist review remains mandatory.

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
- `clinical_validation_status`: `not_validated`
- `requires_pharmacist_review`: `true`
- `patient_facing_allowed`: `false`
- `counseling_draft_allowed`: `true`
- All profiles are draft educational placeholder content.
- No profile is clinically validated.
- No profile is allowed for patient-facing output without pharmacist review.
- Retrieved RAG chunks can expose governance metadata for source grounding review.
- The current KB is suitable for local workflow and evaluation scaffolding only.

Governance files:

- `data/drug_profiles/drug_registry.json`
- `data/drug_profiles/source_catalog.json`

Source catalog categories:

- `regulatory_label`
- `official_drug_monograph`
- `national_formulary`
- `peer_reviewed_reference`
- `local_placeholder`

## 6. Evaluation Status

Current verification status:

- Backend tests: 169 passed, 1 skipped.
- RAG evaluation: 46/46 passed.
- Retrieval strategy evaluation: PASS, recommended default `existing_default`.
- Safety rules report: PASS, 10/10 synthetic scenarios.
- OCR evaluation: 18/18 passed, including 10 fixture-backed cases.
- E2E OCR-to-RAG workflow evaluation: 10/10 passed.
- E2E trace export: 10 synthetic traces exported.
- E2E trace report: PASS, unverified OCR downstream use blocked in 10/10 traces.
- Dashboard workflow polish: frontend typecheck/build passed.
- OCR fixture inspection: PASS for six readable synthetic PNG fixtures.
- Optional Tesseract benchmark: command runs; current runtime reports skipped because `tesseract_binary` is not detected on `PATH`.
- OCR activation policy report: PASS.
- KB report: PASS, 0 blocking issues.
- KB governance report: PASS, 0 blocking issues and expected draft/placeholder warnings.
- OCR provider report: PASS, 2 active local providers allowed in prototype mode and quality-gate eligible; Tesseract adapter shown as inactive and not prototype-allowed.
- OCR candidate report: PASS, 5 candidates with 2 prototype allowed, Tesseract adapter-defined but inactive, and cloud OCR blocked.
- Frontend typecheck: passed.
- Frontend build: passed.

Verification commands:

```bash
cd backend && python -m pytest
cd backend && python scripts/generate_ocr_fixtures.py
cd backend && python scripts/inspect_ocr_fixtures.py
cd backend && python scripts/evaluate_rag.py
cd backend && python scripts/evaluate_retrieval_strategies.py
cd backend && python scripts/kb_report.py
cd backend && python scripts/kb_governance_report.py
cd backend && python scripts/safety_rules_report.py
cd backend && python scripts/evaluate_ocr.py
cd backend && python scripts/ocr_provider_report.py
cd backend && python scripts/ocr_candidate_report.py
cd backend && python scripts/ocr_activation_policy_report.py
cd backend && python scripts/evaluate_e2e_workflow.py
cd backend && python scripts/export_e2e_traces.py
cd backend && python scripts/e2e_trace_report.py
cd backend && python scripts/benchmark_tesseract_ocr.py
cd frontend && npm.cmd run typecheck
cd frontend && npm.cmd run build
```

## 7. Safety and Privacy Boundaries

Current non-negotiable boundaries:

- Pharmacist review is required.
- Outputs are draft-only.
- The system must not provide final medical advice.
- Unknown medications must not be guessed.
- Weak or missing local context returns insufficient knowledge-base context.
- Retrieval diagnostics and strategy comparisons are engineering checks, not clinical validation.
- Medication safety-rule findings are pharmacist-support prompts, not clinical decisions.
- Interaction and contraindication checks are explicitly unavailable in this prototype.
- No real patient data belongs in the repository.
- Uploaded images are not stored by default.
- OCR output is unverified.
- OCR text must be corrected or confirmed by a pharmacist before analysis.
- End-to-end workflow evaluation uses corrected text only for downstream prescription analysis, RAG, and counseling.
- Workflow traces show the correction boundary and blocked unverified OCR downstream use.
- Dashboard shows OCR unverified status, correction boundary, source grounding, draft-only counseling, and pharmacist review required.
- Synthetic trace records do not store raw image bytes or real patient data.
- Current KB profiles are draft placeholder educational content and not clinically validated.
- Current KB profiles are not allowed for patient-facing output.
- Counseling drafts are allowed only as pharmacist-review-required support.
- KB governance reports are engineering checks, not clinical validation.
- Patient-facing output remains disabled by KB governance and safety-rule policy.
- Current OCR providers are local, non-networked, and non-storing.
- Tesseract adapter exists only as disabled/benchmark-only scaffolding and is not active OCR.
- Tesseract is blocked in default workflow and can only be used in explicit prototype workflow mode when policy gates pass.
- Explicit external OCR provider names are rejected in prototype mode.
- Planned OCR candidates are metadata only and must not be activated accidentally.
- Cloud OCR is disallowed for prototype mode pending formal privacy review.
- OCR quality gates are engineering checks only, not clinical validation.
- Possible identifiers are flagged as possible identifiers, not confirmed PII.
- No external APIs are used.
- No clinical validation is claimed.

## 8. Important Files and Directories

- `backend/app/main.py`: FastAPI application factory and route wiring.
- `backend/app/api/`: HTTP route modules for health, prescriptions, drugs, counseling, RAG, and OCR.
- `backend/app/services/`: Application services for extraction, safety, lookup, counseling, RAG orchestration, OCR, and OCR audit.
- `backend/app/rag/`: Local TF-IDF RAG components, generation, citation validation, RAG evaluation, retrieval diagnostics, strategy comparison, and query classification.
- `backend/app/safety/`: Deterministic medication safety-rule models and rule evaluation.
- `backend/app/kb/`: Drug registry loading, KB validation, governance validation, coverage schema, and future ingestion scaffolding.
- `backend/app/ocr/`: OCR provider interface, local provider implementations, activation policy, safe OCR config, inactive local adapter benchmarking, dependency checks, fixture inspection, evaluation metrics, quality gates, provider candidates, swap-readiness checks, and synthetic OCR evaluation runner logic.
- `backend/app/workflows/`: Synthetic end-to-end workflow evaluation and trace models from OCR-like input through corrected text, prescription analysis, RAG, counseling, and pharmacist review.
- `backend/scripts/`: CLI scripts for RAG evaluation, retrieval strategy evaluation, KB reporting, KB governance reporting, safety-rule reporting, OCR evaluation, OCR provider reporting, OCR candidate reporting, E2E workflow evaluation, trace export, and trace reporting.
- `backend/tests/`: Backend pytest regression tests.
- `frontend/components/`: Pharmacist dashboard UI components, including workflow status, safety review, and source-grounding panels.
- `frontend/lib/`: Frontend API client and shared TypeScript types.
- `data/drug_profiles/`: Draft educational Markdown profiles, drug registry, and source catalog.
- `data/evaluation/`: Synthetic RAG, OCR, E2E workflow datasets, generated synthetic trace records, and synthetic OCR fixtures.
- `docs/`: Architecture, safety, privacy, roadmap, OCR evaluation, retrieval intelligence, medication safety rules, KB scaling/governance, and living project documentation.

## 9. Current Limitations

- Default OCR workflow provider remains mock OCR.
- No real OCR provider is integrated.
- Tesseract adapter is disabled by default and can only run in explicit synthetic benchmark mode or explicit prototype mode when policy gates pass.
- E2E workflow evaluation is synthetic and does not prove clinical validity.
- Workflow traces are synthetic engineering audit artifacts, not production audit logs.
- Dashboard workflow status is a frontend state display, not a production audit record.
- Planned OCR engines are not installed or active; the Tesseract adapter is present but disabled outside explicit benchmark mode.
- No real prescription images are used.
- No persistent audit database exists.
- Retrieval uses local TF-IDF only.
- Retrieval strategy comparison is synthetic and does not validate clinical relevance.
- Medication safety rules are deterministic workflow prompts and do not perform real interaction, contraindication, diagnosis, or appropriateness checking.
- The knowledge base is draft educational placeholder content only.
- Source catalog categories are governance scaffolding only; trusted sources have not been ingested.
- No current drug profile has pharmacist-reviewed source evidence, reviewer role, review timestamp, or clinical validation.
- There is no clinical validation.
- Deployment is not hardened.
- Production authentication and authorization are not implemented.
- Real pharmacy system integration is not implemented.
- Audit retention, access controls, and review sign-off workflows are not production-ready.

## 10. Recommended Next Phases

Proposed roadmap:

- Phase 3D: Demo Packaging, Case Study, and Final Portfolio QA.
- Phase 4A: Trusted Source Ingestion Prototype after source governance approval.
- Phase 4B: Drug Knowledge Graph.
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
