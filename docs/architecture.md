# Architecture

PharmaGuard AI is structured as a pharmacist-in-the-loop copilot. The current implementation includes a local Phase 1 RAG MVP using Markdown drug profiles and TF-IDF retrieval, Phase 1.5 hardening for evaluation and citation validation, Phase 1.6 knowledge base/evaluation expansion, Phase 1.7 controlled knowledge base expansion, Phase 1.8 scalable knowledge base architecture, Phase 2A privacy-safe OCR intake foundation, Phase 2B OCR evaluation/correction audit, Phase 2C OCR provider interface with synthetic fixtures, Phase 2D OCR quality benchmarking/provider swap readiness, Phase 2E OCR provider candidate comparison, and Phase 2F disabled local OCR adapter scaffolding.

## Pipeline

`Prescription Image Upload -> Mock OCR Intake -> Pharmacist OCR Correction + Audit -> Prescription Text Analysis -> Drug Entity Extraction -> Safety Layer -> RAG Retrieval -> Pharmacist Review -> Patient Counseling`

## Stages

1. Prescription Input
   - Current: pharmacist can paste synthetic prescription text or upload a synthetic image for OCR intake.
   - Later: richer image/PDF intake with stricter operational controls.

2. OCR Intake
   - Current: `backend/app/ocr/providers.py` exposes a provider boundary with deterministic local `MockOcrProvider` and `SyntheticFixtureOcrProvider` implementations. `/ocr/extract-image` accepts supported image formats, reads uploads in memory, does not persist images by default, returns unverified text, and flags possible identifier patterns.
   - Current: `TesseractLocalOcrProvider` exists only as a disabled adapter skeleton. It is not active, not prototype-allowed, and does not run OCR.
   - Current: `/ocr/confirm-text` accepts pharmacist-corrected text and returns correction audit metadata. Only corrected text can be manually moved into prescription analysis.
   - Later: validated OCR providers can be swapped behind the same interface after privacy and safety review.

3. Text Extraction
   - Current: simple rule-based cleanup and medication candidate detection from pasted or pharmacist-corrected text.
   - Later: structured extraction with confidence scoring and evaluation.

4. Drug Entity Extraction
   - Current: matches explicit generic names and conservative aliases from the drug registry, with the mock index retained as a compatibility fallback.
   - Later: normalize medication entities to a verified drug vocabulary.

5. Safety Layer
   - Current: warns on low confidence, missing patient context, and unknown medication names.
   - Current: OCR output remains unverified and requires pharmacist correction before downstream analysis.
   - Always: final decisions remain with the pharmacist.

6. RAG Retrieval
   - Current: loads enabled local Markdown profiles from `data/drug_profiles/`, chunks them by headings and paragraphs, embeds chunks with local TF-IDF, stores vectors in memory, and retrieves top-k medication-specific context.
   - Phase 1.5: validates retrieved source metadata, checks generated citations, and runs synthetic RAG evaluation cases before OCR work begins.
   - Phase 1.8: uses `drug_registry.json` for supported identities, aliases, review status, source status, and RAG enablement metadata.
   - Later: replace or supplement TF-IDF with dense vector retrieval after baseline evaluation.

7. Pharmacist Review
   - Current: UI requires a pharmacist confirmation action before counseling generation.
   - Later: support audit trails and structured review decisions.

8. Patient Counseling
   - Current: generates a grounded draft from retrieved Markdown context after pharmacist confirmation.
   - Later: add richer citation checks, evaluation gates, and approved reference sources.

## Phase 1 Local RAG

The local RAG MVP avoids external APIs and model downloads. It uses:

- Markdown profiles in `data/drug_profiles/`.
- `chunker.py` to preserve `drug_name`, `source_file`, `section_title`, and `chunk_id` metadata.
- `embedder.py` with `scikit-learn` TF-IDF as the default embedder.
- `vector_store.py` for an in-memory index.
- `retriever.py` for medication-aware top-k retrieval with a minimum relevance threshold.
- `generator.py` for deterministic pharmacist-support drafts based only on retrieved chunks.

If no local chunk passes the threshold, the backend returns `insufficient knowledge base context` rather than guessing.

## Phase 2A OCR Intake Foundation

Phase 2A adds OCR as an assistive input layer, not as a source of final truth.

- `app/schemas/ocr.py` defines upload, extracted text, correction, and privacy warning contracts.
- `app/services/ocr_service.py` defines a provider-style OCR boundary and `MockOcrProvider`.
- `app/api/routes_ocr.py` exposes `/ocr/extract-image` and `/ocr/confirm-text`.
- Supported upload types are PNG, JPG, JPEG, and WEBP.
- Uploads are size-limited and read in memory; no image storage is created by default.
- Possible identifier patterns are reported as privacy warnings, not validated facts.
- OCR output is labeled unverified and cannot automatically trigger prescription analysis, RAG, counseling, or drug lookup.
- The frontend shows editable OCR text and requires a pharmacist action before corrected text is placed into the prescription text workflow.

This boundary is designed so a future OCR implementation can be swapped without weakening the downstream pharmacist confirmation gates.

## Phase 2B OCR Evaluation And Correction Audit

Phase 2B adds evaluation and auditability around the mock OCR intake boundary.

- `data/evaluation/ocr_eval_cases.json` contains 10 synthetic text-only OCR cases.
- `app/ocr/evaluation.py` provides deterministic character error rate, word error rate, token overlap, medication term hit, and privacy warning match metrics.
- `app/services/ocr_audit_service.py` builds returned correction audit metadata without database persistence.
- `backend/scripts/evaluate_ocr.py` runs the synthetic OCR evaluation and prints pass/fail status, average error rates, medication detection summary, and privacy warning summary.
- `/ocr/confirm-text` returns `correction_audit` with changed status, difference metrics, detected supported medication terms, privacy warning categories, and generated timestamp.

The metrics are synthetic engineering checks. They do not validate clinical correctness, OCR production quality, patient identity, or medication appropriateness. OCR output remains unverified until pharmacist correction and still does not automatically invoke prescription analysis, RAG, counseling, or lookup.

## Phase 2C OCR Provider Interface And Synthetic Fixtures

Phase 2C separates OCR provider behavior from OCR service orchestration.

- `backend/app/ocr/providers.py` defines `BaseOcrProvider`, `MockOcrProvider`, and `SyntheticFixtureOcrProvider`.
- Providers expose `provider_name`, `supports_content_type`, `is_external_provider`, `stores_images`, `requires_network`, and supported content types.
- `backend/app/services/ocr_service.py` performs safe provider selection and rejects explicit external provider names.
- Current provider metadata is returned from `/ocr/extract-image`.
- `data/evaluation/ocr_fixtures/` contains approved synthetic PNG fixtures for evaluation plumbing.
- `backend/scripts/ocr_provider_report.py` reports provider readiness and prototype-mode safety status.

No external OCR provider is enabled. The fixture provider is filename-driven and exists to test provider plumbing and fixture-backed evaluation only.

## Phase 2D OCR Quality Benchmarking And Provider Swap Readiness

Phase 2D adds provider-specific benchmark gates before any real OCR provider is considered.

- `backend/app/ocr/quality_gates.py` defines prototype OCR quality gate checks.
- OCR evaluation now includes 18 synthetic cases, including 10 fixture-backed cases.
- Provider summaries report cases, pass/fail counts, average CER/WER, and quality gate metrics.
- Quality gates check maximum average character error rate, maximum average word error rate, minimum token overlap, medication detection, privacy-warning matching, unverified output status, and provider safety metadata.
- Provider report output includes quality gate eligibility and prototype allowed status.

These gates are engineering swap-readiness checks. They do not validate clinical correctness or production OCR quality.

## Phase 2E OCR Provider Candidate Comparison

Phase 2E adds a metadata-only decision layer for future OCR providers.

- `data/evaluation/ocr_provider_candidates.json` records implemented, planned, and disallowed OCR candidates.
- `backend/app/ocr/provider_candidates.py` loads candidate metadata and summarizes readiness.
- `backend/app/ocr/provider_swap_readiness.py` checks prototype blockers, future-evaluation readiness, warnings, and next steps.
- `backend/scripts/ocr_candidate_report.py` prints the provider candidate matrix.

No candidate provider runs OCR through this layer. Tesseract has an inactive adapter skeleton as of Phase 2F, while EasyOCR remains metadata-only. Cloud OCR is disallowed for prototype mode because it requires network access and privacy review.

## Phase 2F Optional Local OCR Adapter Spike

Phase 2F adds a disabled-by-default Tesseract adapter boundary without installing or activating Tesseract.

- `backend/app/ocr/local_tesseract_provider.py` defines `TesseractLocalOcrProvider`.
- `backend/app/ocr/provider_dependencies.py` checks optional local dependencies without installing packages or calling the network.
- `backend/app/services/ocr_service.py` rejects explicit Tesseract requests with a controlled prototype-mode error.
- Provider and candidate reports show Tesseract as adapter-defined but inactive, with dependency status and required next steps.

Mock and synthetic fixture providers remain the only active OCR providers. OCR output remains unverified, and pharmacist correction remains mandatory.

## Phase 1.7 Controlled Knowledge Base Expansion

The local knowledge base now includes 15 Markdown profiles:

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

Each profile uses consistent sections: Overview, Common Uses, General Counseling Points, Safety Notes, When to Refer to Pharmacist or Physician, Patient Questions to Ask, and Knowledge Base Limitations.

Alias handling remains conservative. Explicit aliases in the local mock index can map to supported medications, but condition-only or class-only queries do not choose a medication. For example, `ventolin` can resolve to salbutamol and `glucophage` can resolve to metformin, while a condition-only query without a named medication returns insufficient context.

## Phase 1.8 Scalable Knowledge Base Architecture

Phase 1.8 adds a governed registry around the local Markdown profiles without replacing the RAG architecture.

- `data/drug_profiles/drug_registry.json` contains one entry for each of the 15 current profiles.
- Registry entries track generic name, display name, profile file, aliases, general class labels, context tags, `review_status`, `source_status`, source notes, safety notes, and `enabled_for_rag`.
- Current profiles are marked `draft` and `placeholder_educational`, with no reviewer or review date. They are not clinically validated.
- `app/kb/registry.py` loads the registry, normalizes explicit names and aliases, detects duplicate aliases, exposes lookup by generic name or alias, and lists enabled profiles.
- `app/kb/validator.py` checks required metadata, required Markdown sections, profile-file existence, unique aliases, disabled profiles, and unreviewed draft profiles.
- `backend/scripts/kb_report.py` prints coverage and validation summaries for local governance review.
- `app/kb/ingestion_plan.py` contains stubs for future structured ingestion, draft creation, pharmacist review, approval, and rejection. It performs no external calls.

This phase prepares the project for hundreds of future medication profiles without encouraging hundreds of manually maintained Markdown files as the long-term architecture. Future ingestion should preserve provenance and require pharmacist approval before enabling RAG.

## Phase 1.5 RAG Hardening

Phase 1.5 through Phase 1.8 keep the same local architecture and add safeguards around it:

- `data/evaluation/rag_eval_cases.json` defines 46 synthetic supported, alias, unknown, weak-query, condition-only, unsupported-information, exact-dose, final-advice, and mixed prescription-like cases.
- `app/rag/evaluation.py` runs cases through the existing retriever/generator pipeline.
- `app/rag/citation_validator.py` verifies chunk metadata and generated source references.
- `backend/scripts/evaluate_rag.py` prints pass/fail status and summaries.

Evaluation metrics:

- `top_k_hit`: the expected medication appears in the retrieved top-k context, or no context is returned when no medication is expected.
- `source_file_hit`: expected Markdown source files are present.
- `section_hit`: expected Markdown sections are present.
- `insufficient_context_correct`: unknown or weak-context cases are correctly marked insufficient.
- Generation safety checks confirm required terms, forbidden term absence, draft/pharmacist-review framing, no unsupported unavailable information, no final-advice wording, and valid citations.

Current TF-IDF limitations:

- Retrieval depends on lexical overlap and aliases from local metadata.
- It can miss semantically related wording if terms differ.
- It has no clinical reasoning capability and should not be treated as validation.

Dense retrieval is a documented future option only. It is deferred until the TF-IDF baseline and KB registry governance have stronger evaluation coverage and documented failure modes. Phase 2A adds only the privacy-safe OCR intake boundary and mock provider; production OCR remains future work.

## Backend Modules

- `app/api`: FastAPI routes.
- `app/schemas`: Pydantic request/response contracts.
- `app/services`: prescription, safety, lookup, counseling, and RAG orchestration logic.
- `app/ocr`: local OCR provider interface, provider implementations, evaluation metrics, and synthetic evaluation runner logic.
- `app/rag`: local TF-IDF RAG components, evaluation, and citation validation.
- `app/kb`: registry loading, validation, coverage reporting models, and future ingestion scaffolding.
- `app/sample_data`: local mock drug index.

## Frontend Modules

- `app`: Next.js app router pages and global styles.
- `components`: pharmacy dashboard panels.
- `lib`: API client and shared TypeScript types.
