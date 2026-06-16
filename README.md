<img width="2172" height="724" alt="ChatGPT Image Jun 15, 2026, 10_24_42 PM" src="https://github.com/user-attachments/assets/350fd7d5-9502-48ca-8c68-e5312629789a" />

## PharmaGuard AI

PharmaGuard AI is a pharmacist-centered AI copilot foundation for prescription text review, trusted medication information retrieval, patient counseling note drafting, and safety-first workflow enforcement.

This repository is being developed incrementally toward a pharmacy-ready architecture, but the current implementation uses synthetic data and local placeholder knowledge only. It is not a medical device, does not diagnose, and must never make final medical decisions.

## Problem Statement

Pharmacists often need to interpret incomplete prescription text, verify medication context, identify missing patient details, and prepare clear counseling notes under time pressure. AI can help organize information, but unsafe automation can introduce risk if it appears to replace professional judgment.

## Solution

PharmaGuard AI is designed as a review-first copilot:

- Extract possible medication entities from prescription text.
- Accept prescription image uploads through a privacy-safe OCR intake boundary.
- Require pharmacist correction before OCR text can become prescription text.
- Retrieve local trusted medication profile placeholders through a Phase 1 TF-IDF RAG workflow.
- Surface missing patient context and confidence warnings.
- Require pharmacist confirmation before generating counseling notes.
- Keep every output framed as a draft for pharmacist review.

## Architecture

Current scaffold:

- `backend/`: FastAPI API, services, schemas, tests, and local RAG modules.
- `frontend/`: Next.js pharmacist dashboard with Tailwind CSS.
- `data/`: synthetic prescriptions, draft drug profiles, the drug registry, and evaluation templates.
- `docs/`: architecture, safety, privacy, roadmap, and challenge planning documents.

Current pipeline:

`Prescription Image Upload -> Mock OCR Intake -> Pharmacist OCR Correction -> Prescription Text Analysis -> Drug Entity Extraction -> Safety Layer -> RAG Retrieval -> Pharmacist Review -> Patient Counseling`

## Safety-First Principles

- Pharmacist stays in control.
- AI output is draft support only.
- Low confidence always requires review.
- Unknown medication names are not guessed.
- OCR output is unverified and cannot move downstream until pharmacist correction.
- Uploaded prescription images are not stored by default.
- Missing age, pregnancy status, allergies, or current medication context triggers a warning.
- No real patient data belongs in this repository.

## Current MVP Scope

Implemented now:

- FastAPI app with health, prescription analysis, drug lookup, and counseling endpoints.
- Mock extraction and safety services.
- Local Markdown drug knowledge base.
- Phase 1 local TF-IDF RAG: Markdown loading, chunking, in-memory indexing, retrieval, and grounded draft generation.
- Phase 1.5 RAG hardening: synthetic RAG evaluation cases, citation validation, unsupported-claim regression tests, and a CLI evaluation runner.
- Phase 1.6 knowledge base and evaluation expansion: seven local drug profiles and 20 synthetic RAG evaluation cases.
- Phase 1.7 controlled knowledge base expansion: 15 local drug profiles and 46 synthetic RAG evaluation cases.
- Phase 1.8 scalable knowledge base architecture: structured drug registry, KB validation, coverage reporting, and safe future ingestion stubs.
- Phase 2A privacy-safe OCR intake foundation: image upload route, mock OCR provider, possible identifier warnings, and pharmacist correction workflow.
- Phase 2B OCR evaluation and correction audit: synthetic OCR cases, deterministic text-quality metrics, and returned pharmacist correction audit metadata.
- Phase 2C OCR provider interface and synthetic image fixtures: local provider metadata, synthetic fixture provider, fixture-backed OCR evaluation, and provider readiness report.
- Phase 2D OCR quality benchmarking and provider swap readiness: expanded synthetic fixtures, provider-level benchmark summaries, and prototype quality gates.
- Phase 2E OCR provider candidate comparison: metadata-only candidate registry, readiness matrix, and candidate report for future provider decisions.
- Phase 2F optional local OCR provider adapter spike: disabled-by-default Tesseract adapter and local dependency checks.
- Phase 2G end-to-end OCR-to-RAG workflow evaluation: synthetic workflow cases proving corrected text is the downstream boundary.
- Phase 2H workflow traceability and pharmacist review audit records: deterministic synthetic traces for safe workflow explainability.
- Phase 2I pharmacist dashboard workflow polish: visible workflow statuses, safety indicators, and source-grounding summary.
- Phase 2J local Tesseract OCR benchmarking: optional synthetic-fixture benchmark path for the disabled local adapter.
- Phase 2K OCR-readable synthetic fixtures and Tesseract benchmark diagnostics.
- Phase 2L-M controlled OCR activation policy and safe explicit Tesseract prototype mode.
- Phase 3A knowledge base governance upgrade: explicit source/review/clinical-validation metadata, source catalog, governance report, and source-aware RAG metadata.
- Phase 3B-C retrieval intelligence and medication safety rules: deterministic query classification, retrieval diagnostics, strategy comparison, safety-rule findings, and trusted-source/review workflow plans.
- Direct `POST /rag/query` endpoint.
- Next.js dashboard that calls backend endpoints.
- Pytest coverage for core placeholder behavior, RAG retrieval, citation validation, KB registry validation, OCR intake, and safety regressions.

Not implemented yet:

- Production OCR.
- External OCR providers.
- Active Tesseract or EasyOCR OCR.
- Default Tesseract OCR.
- Prescription image storage.
- External medical APIs.
- Dense embeddings or persistent vector database.
- Production clinical validation.
- Real patient data handling.

## Supported Local Knowledge Base

Current local Markdown profiles:

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

`data/drug_profiles/drug_registry.json` is now the preferred source of truth for supported generic names, aliases, review status, source status, governance metadata, and whether a profile is enabled for local RAG. All 15 current profiles are marked `review_status: draft`, `source_status: placeholder_educational`, `clinical_validation_status: not_validated`, `requires_pharmacist_review: true`, `patient_facing_allowed: false`, and `counseling_draft_allowed: true`; this makes clear that the current content is educational placeholder material, not clinical validation.

`data/drug_profiles/source_catalog.json` defines source categories and requirements for future trusted-source ingestion. Run `python scripts/kb_governance_report.py` from `backend/` to review governance status. A passing governance report is an engineering governance check, not clinical validation.

Supported aliases are explicit and conservative, such as `acetaminophen -> paracetamol`, `ventolin -> salbutamol`, `glucophage -> metformin`, `norvasc -> amlodipine`, `synthroid -> levothyroxine`, `voltaren -> diclofenac`, and `nexium -> esomeprazole`. Condition-only queries and broad classes such as `antibiotic`, `painkiller`, or `antihistamine` do not map to a medication.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/health`.

Example local RAG query:

```bash
curl -X POST http://localhost:8000/rag/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"paracetamol 500mg counseling\",\"top_k\":5}"
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` if the backend runs on a different host or port.

## Phase 2A OCR Intake

`POST /ocr/extract-image` accepts PNG, JPG, JPEG, and WEBP uploads, rejects unsupported file types, limits upload size, and returns unverified mock OCR text. Images are read in memory and are not persisted by default.

`POST /ocr/confirm-text` accepts pharmacist-corrected OCR text and returns `can_send_to_analysis: true`. The backend does not automatically send OCR output to prescription analysis, RAG, counseling, or drug lookup. The frontend follows the same rule: only the corrected text button can populate the prescription text panel.

The Phase 2A mock OCR provider is deterministic and local. Future OCR providers can be swapped behind the same service interface after privacy review, validation, and pharmacist workflow review.

Phase 2B adds OCR evaluation and correction audit metadata. `POST /ocr/confirm-text` now returns a `correction_audit` object with changed/unchanged status, character error rate, word error rate, detected supported medication terms, privacy warning categories, and a generated timestamp. This audit is returned directly and is not persisted to a database.

Phase 2C adds a local OCR provider interface with safe provider metadata. Current providers are `mock_ocr_phase_2a` and `synthetic_fixture_phase_2c`; both are local, non-networked, and non-storing. Synthetic fixture-backed OCR evaluation uses approved files under `data/evaluation/ocr_fixtures/`.

Phase 2D expands OCR benchmarking to 18 synthetic cases, including 10 fixture-backed cases. Provider quality gates check benchmark error rates, token overlap, medication term detection, privacy-warning matching, non-networked/non-storing provider metadata, and unverified output status. These gates are swap-readiness checks only, not clinical validation.

Phase 2E adds a metadata-only OCR provider candidate matrix. Tesseract and EasyOCR are documented as planned local candidates; no OCR engine packages are installed or activated. Cloud OCR remains disallowed for prototype mode pending formal privacy review.

Phase 2F adds a `tesseract_local_candidate` adapter and dependency checks without installing or activating Tesseract. The adapter is disabled by default, not prototype-allowed, and returns a controlled unavailable status if requested through the normal OCR flow.

Phase 2G adds synthetic end-to-end OCR-to-RAG workflow evaluation. It verifies that unverified OCR is not sent downstream, pharmacist-corrected text can be analyzed, supported medications retrieve source-backed RAG context, unknown medications remain insufficient context, and counseling drafts stay pharmacist-support only.

Phase 2H adds workflow traceability for synthetic E2E cases. Trace records show OCR unverified status, blocked unverified downstream use, pharmacist correction, corrected-text analysis, RAG source checks, draft counseling status, and pharmacist review requirement. Generated traces are deterministic synthetic artifacts under `data/evaluation/generated/e2e_traces.json`; they do not store raw image bytes or real patient data.

Phase 2I improves the dashboard workflow display. The UI now shows ordered workflow statuses, OCR correction boundary messaging, compact safety/review indicators, source-grounding metrics, and pharmacist review reminders without changing backend behavior.

Phase 2J adds optional local Tesseract benchmarking against synthetic PNG fixtures only. Tesseract remains disabled by default, is not the default provider, and is not prototype-allowed. If local dependencies are missing, the benchmark exits successfully with a clear skipped status. Benchmark metrics are engineering checks only, not clinical validation.

Phase 2K replaces invalid tiny fixture PNGs with OCR-readable synthetic text images and adds fixture inspection plus richer benchmark diagnostics.

Phase 2L-M adds a controlled OCR activation policy. The safe default provider remains `mock_ocr_phase_2a`. Tesseract is blocked in `default_workflow`, allowed for `benchmark` only when dependencies are available, and allowed for `prototype_explicit` only when explicit enablement and recorded benchmark gates are satisfied. Tesseract is still not production allowed and never bypasses pharmacist correction.

## Testing

```bash
cd backend
python -m pytest
```

Run the local RAG evaluation:

```bash
cd backend
python scripts/evaluate_rag.py
```

Run retrieval strategy comparison:

```bash
cd backend
python scripts/evaluate_retrieval_strategies.py
```

Run the local knowledge-base coverage report:

```bash
cd backend
python scripts/kb_report.py
```

Run the knowledge-base governance report:

```bash
cd backend
python scripts/kb_governance_report.py
```

Run deterministic medication safety-rule scenarios:

```bash
cd backend
python scripts/safety_rules_report.py
```

Run the synthetic OCR evaluation:

```bash
cd backend
python scripts/evaluate_ocr.py
```

Run the OCR provider readiness report:

```bash
cd backend
python scripts/ocr_provider_report.py
```

Run the OCR candidate comparison report:

```bash
cd backend
python scripts/ocr_candidate_report.py
```

Run the OCR activation policy report:

```bash
cd backend
python scripts/ocr_activation_policy_report.py
```

Run the end-to-end OCR-to-RAG workflow evaluation:

```bash
cd backend
python scripts/evaluate_e2e_workflow.py
```

Export synthetic workflow traces:

```bash
cd backend
python scripts/export_e2e_traces.py
```

Run the workflow trace report:

```bash
cd backend
python scripts/e2e_trace_report.py
```

Run the optional local Tesseract benchmark:

```bash
cd backend
python scripts/benchmark_tesseract_ocr.py
```

The evaluation currently contains 46 synthetic cases. It reports retrieval checks (`top_k_hit`, `source_file_hit`, `section_hit`, `insufficient_context_correct`) and generation safety checks for required terms, forbidden terms, draft/pharmacist-review framing, unavailable information, and fabricated citations.

Retrieval strategy evaluation compares `existing_default`, `lexical_overlap`, `metadata_boosted`, and `hybrid_local`. The current default retriever remains `existing_default`; comparison metrics are engineering checks only and do not validate clinical correctness.

The OCR evaluation currently contains 18 synthetic cases, including 10 fixture-backed cases, and reports character error rate, word error rate, medication term detection, privacy-warning matching, provider-level summaries, and quality gate status. The optional Tesseract benchmark uses only synthetic image fixtures and is skipped when local Tesseract dependencies are unavailable. The E2E workflow evaluation currently contains 10 synthetic cases covering corrected-text handoff into prescription analysis, RAG, and counseling. Trace export currently produces 10 deterministic synthetic traces. These are engineering checks for the OCR workflow, not clinical validation.

The KB report summarizes profile counts, aliases, review/source status, missing sections, alias conflicts, disabled profiles, and unreviewed draft profiles. The KB governance report summarizes source/review/clinical-validation status, patient-facing restrictions, counseling draft allowance, pharmacist review requirements, source catalog categories, blockers, and warnings. The safety rules report exercises deterministic workflow-support rules such as missing dose/frequency/duration/route, unsupported medication text, possible identifiers, placeholder KB context, and patient-facing output blocks. Dense retrieval remains deferred until the TF-IDF baseline and KB governance are stronger. Production OCR and external OCR providers remain deferred.

## Future Roadmap

See [docs/roadmap.md](docs/roadmap.md).

For the living current-state summary, see [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md). For future Codex phase rules, see [docs/AI_DEVELOPMENT_PROTOCOL.md](docs/AI_DEVELOPMENT_PROTOCOL.md). For KB governance, see [docs/kb_governance.md](docs/kb_governance.md). For retrieval intelligence, see [docs/retrieval_intelligence.md](docs/retrieval_intelligence.md). For medication safety rules, see [docs/medication_safety_rules.md](docs/medication_safety_rules.md). For trusted-source planning, see [docs/trusted_source_ingestion_plan.md](docs/trusted_source_ingestion_plan.md). For pharmacist review workflow planning, see [docs/pharmacist_review_workflow.md](docs/pharmacist_review_workflow.md). For OCR provider boundaries, see [docs/ocr_provider_strategy.md](docs/ocr_provider_strategy.md). For OCR activation policy, see [docs/ocr_activation_policy.md](docs/ocr_activation_policy.md). For OCR candidate comparison, see [docs/ocr_candidate_comparison.md](docs/ocr_candidate_comparison.md). For the disabled local adapter plan, see [docs/local_ocr_adapter_plan.md](docs/local_ocr_adapter_plan.md). For optional Tesseract benchmarking, see [docs/tesseract_benchmarking.md](docs/tesseract_benchmarking.md). For E2E workflow evaluation, see [docs/e2e_workflow_evaluation.md](docs/e2e_workflow_evaluation.md). For workflow traceability, see [docs/workflow_traceability.md](docs/workflow_traceability.md). For dashboard workflow notes, see [docs/pharmacist_dashboard_workflow.md](docs/pharmacist_dashboard_workflow.md).

## Data Warning

Only synthetic prescriptions are allowed in this repository. Do not commit patient names, phone numbers, IDs, addresses, clinic identifiers, prescription images, or any other real patient information.
