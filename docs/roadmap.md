# Roadmap

For the living project status, see [PROJECT_STATE.md](PROJECT_STATE.md). Future phases must follow [AI_DEVELOPMENT_PROTOCOL.md](AI_DEVELOPMENT_PROTOCOL.md) and update `docs/PROJECT_STATE.md` before handoff.

## Phase 0: Scaffolding - Complete

- Create repository structure.
- Add FastAPI placeholder endpoints.
- Add Next.js pharmacist dashboard.
- Add synthetic data and safety documentation.
- Add initial pytest coverage.

## Phase 1: RAG MVP - Complete

- Load local Markdown drug profiles. Complete.
- Chunk documents by headings and paragraphs with source metadata. Complete.
- Generate local TF-IDF embeddings. Complete.
- Retrieve top-k context snippets with a relevance threshold. Complete.
- Produce grounded pharmacist-support draft responses with local citations. Complete.

## Phase 1.5: RAG Hardening & Evaluation - Complete

- Add synthetic RAG evaluation cases for supported, alias, unknown, weak-query, unsupported-information, and mixed prescription-like scenarios. Complete.
- Add a CLI RAG evaluation runner. Complete.
- Add citation validation for retrieved chunk metadata and generated source references. Complete.
- Add unsupported-claim and fabricated-citation regression tests. Complete.
- Keep dense retrieval deferred until the TF-IDF baseline has stronger evidence. Complete.

## Phase 1.6: Knowledge Base & Evaluation Expansion - Complete

- Add local Markdown profiles for cetirizine, loratadine, omeprazole, and salbutamol. Complete.
- Add conservative mock aliases for supported medications. Complete.
- Expand synthetic RAG evaluation coverage to 20 cases. Complete.
- Add condition-only, final-advice, and exact-dose prompt coverage. Complete.
- Keep OCR deferred to Phase 2 and dense retrieval deferred until the TF-IDF baseline is stronger. Complete.

## Phase 1.7: Controlled Knowledge Base Expansion - Complete

- Add local Markdown profiles for metformin, amlodipine, levothyroxine, azithromycin, simvastatin, diclofenac, esomeprazole, and aspirin. Complete.
- Increase local profile coverage to 15 supported medications. Complete.
- Add conservative aliases including glucophage, norvasc, synthroid, voltaren, nexium, zocor, zithromax, and acetylsalicylic acid. Complete.
- Expand synthetic RAG evaluation coverage to 46 cases. Complete.
- Keep condition-only queries from mapping to arbitrary medications. Complete.
- Keep OCR deferred to Phase 2 and dense retrieval deferred. Complete.

## Phase 1.8: Scalable Knowledge Base Architecture - Complete

- Add `drug_registry.json` with one structured metadata entry for each of the 15 current profiles. Complete.
- Mark current profiles as draft educational placeholders, not clinically validated content. Complete.
- Add registry loading, generic lookup, alias lookup, enabled-profile listing, missing-profile tracking, and duplicate-alias detection. Complete.
- Add profile validation for required metadata, required Markdown sections, source status, review status, alias conflicts, disabled profiles, and unreviewed draft profiles. Complete.
- Add `python scripts/kb_report.py` for coverage and validation reporting. Complete.
- Add future ingestion stubs that create draft records and require pharmacist review without calling external APIs. Complete.
- Keep OCR deferred to Phase 2 and dense retrieval deferred. Complete.

## Phase 2A: Privacy-Safe OCR Intake Foundation - Complete

- Add OCR schemas for unverified extraction, pharmacist correction, and privacy warnings. Complete.
- Add local mock OCR provider behind a provider-style service boundary. Complete.
- Add `/ocr/extract-image` with supported image validation, size guard, no default storage, and possible identifier warnings. Complete.
- Add `/ocr/confirm-text` so corrected text can be explicitly moved into prescription analysis. Complete.
- Add frontend image upload and pharmacist correction workflow. Complete.
- Keep OCR output separate from RAG, counseling, and prescription analysis until pharmacist confirmation. Complete.

## Phase 2B: OCR Evaluation & Pharmacist Correction Audit - Complete

- Add 10 synthetic OCR evaluation cases. Complete.
- Add deterministic text-quality metrics: character error rate, word error rate, and token overlap. Complete.
- Add medication term hit and privacy warning match checks for synthetic OCR cases. Complete.
- Return pharmacist correction audit metadata from `/ocr/confirm-text`. Complete.
- Add OCR evaluation runner at `python scripts/evaluate_ocr.py`. Complete.
- Keep OCR output separate from RAG, counseling, lookup, and prescription analysis until pharmacist confirmation. Complete.
- Avoid persistent audit storage, real prescription data, and external OCR APIs. Complete.

## Phase 2C: OCR Provider Interface & Synthetic Image Fixtures - Complete

- Add `BaseOcrProvider`, `MockOcrProvider`, and `SyntheticFixtureOcrProvider`. Complete.
- Add safe OCR provider selection and explicit external-provider rejection. Complete.
- Return provider safety metadata from OCR extraction responses. Complete.
- Add synthetic OCR fixture files under `data/evaluation/ocr_fixtures/`. Complete.
- Connect OCR evaluation to text-only and fixture-backed cases. Complete.
- Add OCR provider readiness report at `python scripts/ocr_provider_report.py`. Complete.
- Keep external OCR APIs, production OCR, and image storage deferred. Complete.

## Phase 2D: OCR Quality Benchmarking and Provider Swap Readiness - Complete

- Add richer synthetic fixture coverage with PNG fixtures and descriptor fixtures. Complete.
- Expand OCR evaluation to 18 synthetic cases with 10 fixture-backed cases. Complete.
- Add provider-specific quality gates and privacy checks. Complete.
- Add provider-level OCR benchmark summaries and gate results. Complete.
- Keep OCR output unverified and pharmacist correction mandatory. Complete.
- Keep production OCR, external APIs, and real prescription images deferred. Complete.

## Phase 2E: OCR Provider Candidate Comparison & Swap Readiness Matrix - Complete

- Add OCR provider candidate registry. Complete.
- Add candidate loader and readiness summaries. Complete.
- Add provider swap-readiness checks for prototype blockers and future evaluation. Complete.
- Add OCR candidate comparison report. Complete.
- Document local planned candidates without activating them. Complete.
- Keep cloud OCR blocked for prototype mode pending privacy review. Complete.

## Phase 2F: Optional Local OCR Provider Adapter Spike - Complete

- Add `TesseractLocalOcrProvider` behind `BaseOcrProvider`. Complete.
- Keep Tesseract disabled by default and not prototype-allowed. Complete.
- Add local dependency checks for `pytesseract` and the Tesseract binary without installing anything. Complete.
- Update provider and candidate reports with dependency status and inactive-adapter readiness. Complete.
- Keep mock and synthetic fixture providers as the only active OCR providers. Complete.
- Do not integrate cloud OCR without formal review. Complete.

## Phase 2G: End-to-End OCR-to-RAG Workflow Evaluation - Complete

- Add synthetic end-to-end workflow cases. Complete.
- Evaluate OCR output through pharmacist correction, prescription analysis, extraction, RAG retrieval, and counseling drafts. Complete.
- Prove unverified OCR does not go downstream automatically. Complete.
- Check unknown medications, possible identifier warnings, exact-dose prompts, and final-advice prompts. Complete.
- Keep real OCR, Tesseract activation, external APIs, and real prescription data deferred. Complete.

## Phase 2H: Workflow Traceability & Pharmacist Review Audit Records - Complete

- Add structured workflow trace models. Complete.
- Generate traces from synthetic E2E workflow evaluation. Complete.
- Export deterministic synthetic trace records. Complete.
- Add trace report for step, safety flag, pharmacist review, source grounding, and blocked unsafe-flow summaries. Complete.
- Keep traces free of raw image bytes and real patient data. Complete.

## Phase 2I: Pharmacist Dashboard Workflow Polish - Complete

- Add visible ordered workflow status panel. Complete.
- Add compact safety/review indicators. Complete.
- Add source-grounding summary panel. Complete.
- Improve OCR card correction-boundary messaging. Complete.
- Keep backend behavior unchanged and OCR unverified until pharmacist correction. Complete.

## Phase 2J: Local Tesseract OCR Benchmarking with Synthetic Fixtures Only - Complete

- Add explicit benchmark-mode extraction for the disabled Tesseract adapter. Complete.
- Keep Tesseract disabled by default, not prototype-allowed, and not the default provider. Complete.
- Benchmark synthetic image fixtures only and skip descriptor fixtures. Complete.
- Exit gracefully when local dependencies are unavailable. Complete.
- Compare OCR output against expected pharmacist-corrected text with CER, WER, token overlap, medication detection, and privacy-warning checks. Complete.
- Keep provider activation gated by privacy, dependency, workflow, and quality checks. Complete.

## Phase 2K: OCR-Readable Synthetic Fixtures & Tesseract Benchmark Diagnostics - Complete

- Replace invalid tiny PNG fixtures with OCR-readable synthetic text images. Complete.
- Add deterministic fixture generation script. Complete.
- Add fixture inspection script for size, contrast, variation, and blank-image checks. Complete.
- Add Tesseract benchmark diagnostics for raw/normalized text, empty output, preprocessing attempts, medication terms, and privacy warning checks. Complete.
- Keep Tesseract disabled by default and pharmacist correction mandatory. Complete.

## Phase 2L-M: Controlled Local OCR Activation Policy & Safe Tesseract Workflow Mode - Complete

- Add OCR runtime config with safe environment defaults. Complete.
- Add activation policy for default workflow, benchmark, prototype explicit, and production modes. Complete.
- Keep mock OCR as the default provider. Complete.
- Block Tesseract in default workflow and production. Complete.
- Allow Tesseract only for benchmark or explicitly enabled prototype mode when policy gates pass. Complete.
- Add OCR activation policy report. Complete.
- Keep benchmark mode script-only and correction gate mandatory. Complete.

## Phase 3A: Knowledge Base Governance Upgrade - Complete

- Add governance metadata to all 15 current drug registry entries. Complete.
- Keep current profiles draft, placeholder educational, not clinically validated, not patient-facing, and pharmacist-review-required. Complete.
- Add `source_catalog.json` for future source categories and review requirements. Complete.
- Add KB governance validation and `python scripts/kb_governance_report.py`. Complete.
- Integrate governance summary into the existing KB report. Complete.
- Add governance metadata to retrieved RAG source chunks without changing retrieval ranking. Complete.
- Keep RAG outputs pharmacist-support only and avoid clinical validation claims. Complete.

## Phase 2N: Production-Ready OCR Integration Planning

- Add production-ready OCR workflow only after provider validation.
- Define confidence scoring and audit retention policy for OCR output.

## Phase 3: Evaluation

- Build ground truth datasets from synthetic cases.
- Measure extraction precision and recall.
- Track unsafe-output test cases.
- Add regression tests for safety guardrails.

## Phase 4: Drug Knowledge Graph

- Normalize drug entities.
- Model relationships among ingredients, classes, warnings, and counseling topics.
- Add graph-backed lookup experiments.
- Use graph constraints to reduce unsafe guesses.

## Phase 5: Portfolio Polish

- Improve UX and accessibility.
- Add architecture diagrams.
- Add demo script and sample screenshots.
- Add deployment documentation.
- Prepare a concise project case study.
