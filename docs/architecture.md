# Architecture

PharmaGuard AI is structured as a pharmacist-in-the-loop copilot. The current implementation includes a local Phase 1 RAG MVP using Markdown drug profiles and TF-IDF retrieval, Phase 1.5 hardening for evaluation and citation validation, and Phase 1.6 knowledge base/evaluation expansion.

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
   - Phase 1.5: validates retrieved source metadata, checks generated citations, and runs synthetic RAG evaluation cases before OCR work begins.
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

## Phase 1.6 Knowledge Base Expansion

The local knowledge base now includes Markdown profiles for:

- paracetamol
- ibuprofen
- amoxicillin
- cetirizine
- loratadine
- omeprazole
- salbutamol

Each profile uses consistent sections: Overview, Common Uses, General Counseling Points, Safety Notes, When to Refer to Pharmacist or Physician, Patient Questions to Ask, and Knowledge Base Limitations.

Alias handling remains conservative. Explicit aliases in the local mock index can map to supported medications, but condition-only or class-only queries do not choose a medication. For example, `ventolin` can resolve to salbutamol, while an allergy-condition query without a named medication returns insufficient context.

## Phase 1.5 RAG Hardening

Phase 1.5 and Phase 1.6 keep the same local architecture and add safeguards around it:

- `data/evaluation/rag_eval_cases.json` defines 20 synthetic supported, alias, unknown, weak-query, condition-only, unsupported-information, exact-dose, final-advice, and mixed prescription-like cases.
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

Dense retrieval is a documented future option only. It is deferred until the TF-IDF baseline has stronger evaluation coverage and documented failure modes. OCR stays in Phase 2 because image intake and privacy handling should not be mixed with knowledge base and evaluation expansion.

## Backend Modules

- `app/api`: FastAPI routes.
- `app/schemas`: Pydantic request/response contracts.
- `app/services`: prescription, safety, lookup, counseling, and RAG orchestration logic.
- `app/rag`: local TF-IDF RAG components, evaluation, and citation validation.
- `app/sample_data`: local mock drug index.

## Frontend Modules

- `app`: Next.js app router pages and global styles.
- `components`: pharmacy dashboard panels.
- `lib`: API client and shared TypeScript types.
