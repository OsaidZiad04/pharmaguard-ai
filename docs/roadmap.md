# Roadmap

## Phase 0: Scaffolding

- Create repository structure.
- Add FastAPI placeholder endpoints.
- Add Next.js pharmacist dashboard.
- Add synthetic data and safety documentation.
- Add initial pytest coverage.

## Phase 1: RAG MVP

- Load local Markdown drug profiles.
- Chunk documents.
- Generate mock or local embeddings.
- Retrieve top-k context snippets.
- Produce grounded draft responses with citations.

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
