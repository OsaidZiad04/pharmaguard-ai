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

## Phase 2C: OCR Provider Evaluation

- Evaluate local OCR engines or approved provider integrations behind the existing service boundary.
- Add OCR quality evaluation against synthetic image fixtures.
- Add pharmacist correction audit metadata persistence only after privacy controls are reviewed.
- Keep image storage disabled by default until privacy controls are reviewed.

## Phase 2D: Production-Ready OCR Integration

- Add prescription image upload workflow.
- Integrate OCR behind a privacy-safe interface.
- Compare OCR text against pharmacist corrections.
- Add confidence scoring for OCR output.

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
