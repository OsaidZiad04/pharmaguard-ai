# Roadmap

## Phase 0: Scaffolding - Complete

- Create repository structure.
- Add FastAPI placeholder endpoints.
- Add Next.js pharmacist dashboard.
- Add synthetic data and safety documentation.
- Add initial pytest coverage.

## Phase 1: RAG MVP - In Progress

- Load local Markdown drug profiles. Complete.
- Chunk documents by headings and paragraphs with source metadata. Complete.
- Generate local TF-IDF embeddings. Complete.
- Retrieve top-k context snippets with a relevance threshold. Complete.
- Produce grounded pharmacist-support draft responses with local citations. Complete.
- Add more evaluation cases for retrieval quality. Next.
- Add stronger citation validation and unsupported-claim tests. Next.
- Decide whether to add dense retrieval after TF-IDF baseline evaluation. Next.

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
