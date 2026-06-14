# Architecture

PharmaGuard AI is structured as a pharmacist-in-the-loop copilot. The current implementation is a scaffold with mock logic and local placeholder data.

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
   - Current: package-style skeletons for chunking, embedding, vector storage, retrieval, and generation.
   - Later: retrieve grounded snippets from trusted medication references.

7. Pharmacist Review
   - Current: UI requires a pharmacist confirmation action before counseling generation.
   - Later: support audit trails and structured review decisions.

8. Patient Counseling
   - Current: generates a safe placeholder draft based on confirmed pharmacist input.
   - Later: generate grounded, source-backed counseling notes after validation.

## Backend Modules

- `app/api`: FastAPI routes.
- `app/schemas`: Pydantic request/response contracts.
- `app/services`: placeholder business logic.
- `app/rag`: future RAG workflow components.
- `app/sample_data`: local mock drug index.

## Frontend Modules

- `app`: Next.js app router pages and global styles.
- `components`: pharmacy dashboard panels.
- `lib`: API client and shared TypeScript types.
