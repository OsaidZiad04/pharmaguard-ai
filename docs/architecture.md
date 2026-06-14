# Architecture

PharmaGuard AI is structured as a pharmacist-in-the-loop copilot. The current implementation includes a local Phase 1 RAG MVP using Markdown drug profiles and TF-IDF retrieval.

## Pipeline

`Prescription Input -> OCR later -> Text Extraction -> Drug Entity Extraction -> Safety Layer -> RAG Retrieval -> Pharmacist Review -> Patient Counseling`

## Stages

1. Prescription Input
   - Current: pharmacist pastes synthetic prescription text.
   - Later: image/PDF intake with strict privacy controls.

2. OCR Later
   - Current: `ocr_service.py` contains a placeholder.
   - Later: OCR extracts text from uploaded prescription images.

3. Text Extraction
   - Current: simple rule-based cleanup and medication candidate detection.
   - Later: structured extraction with confidence scoring and evaluation.

4. Drug Entity Extraction
   - Current: matches local mock drug names and aliases.
   - Later: normalize medication entities to a verified drug vocabulary.

5. Safety Layer
   - Current: warns on low confidence, missing patient context, and unknown medication names.
   - Always: final decisions remain with the pharmacist.

6. RAG Retrieval
   - Current: loads local Markdown files from `data/drug_profiles/`, chunks them by headings and paragraphs, embeds chunks with local TF-IDF, stores vectors in memory, and retrieves top-k medication-specific context.
   - Later: replace or supplement TF-IDF with dense vector retrieval after evaluation.

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

## Backend Modules

- `app/api`: FastAPI routes.
- `app/schemas`: Pydantic request/response contracts.
- `app/services`: prescription, safety, lookup, counseling, and RAG orchestration logic.
- `app/rag`: local TF-IDF RAG components.
- `app/sample_data`: local mock drug index.

## Frontend Modules

- `app`: Next.js app router pages and global styles.
- `components`: pharmacy dashboard panels.
- `lib`: API client and shared TypeScript types.
