# Roadmap

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

## Phase 1.8: Scalable Knowledge Base Architecture - Next

- Define structured metadata for drug profiles, aliases, sections, and source provenance.
- Add validation tooling for profile completeness and unsafe phrases.
- Explore separating knowledge content from retrieval index construction.
- Prepare for future approved reference ingestion without adding external APIs yet.

## Phase 2: OCR Integration

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
