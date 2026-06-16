# Diagram Prompts And Screenshot Checklist

Do not generate diagrams with real prescription images or patient data. Any generated visual should clearly represent a prototype using synthetic data and draft knowledge-base content.

## System Architecture Diagram

Prompt:

Create a clean technical architecture diagram for "PharmaGuard AI", a pharmacist-centered prescription support prototype. Show a FastAPI backend, Next.js pharmacist dashboard, local Markdown drug knowledge base, drug registry, source catalog, TF-IDF RAG layer, OCR provider interface, synthetic evaluation datasets, and report scripts. Emphasize that all data is local/synthetic, pharmacist review is mandatory, patient-facing output is disabled, and the system is not clinically validated.

Key labels:

- Next.js Pharmacist Dashboard
- FastAPI Backend
- OCR Provider Interface
- Pharmacist Correction Gate
- Prescription Analysis
- Local RAG Retrieval
- KB Governance
- Safety Rules
- Evaluation Reports

## OCR-To-RAG Workflow Diagram

Prompt:

Create a workflow diagram showing prescription image upload or text input flowing through OCR extraction, unverified OCR status, pharmacist correction, prescription analysis, medication extraction, local RAG retrieval, source grounding, draft counseling, and pharmacist final review. Show a blocked arrow from unverified OCR directly to analysis. Include "no image storage by default" and "synthetic data only" notes.

## Safety Governance Diagram

Prompt:

Create a safety governance diagram for PharmaGuard AI showing knowledge-base registry metadata, source catalog, review status, clinical validation status, patient-facing output disabled, pharmacist review required, retrieval diagnostics, and medication safety-rule prompts. Make clear that these are engineering safeguards and not clinical validation.

## Evaluation Pipeline Diagram

Prompt:

Create an evaluation pipeline diagram showing synthetic RAG evaluation, OCR evaluation, retrieval strategy evaluation, KB governance report, safety rules report, E2E workflow evaluation, trace export/report, OCR provider/candidate/activation reports, Tesseract benchmark optional safe skip, project evidence report, and final demo report.

## Dashboard Screenshot Checklist

Capture only synthetic data and local prototype screens:

- Main pharmacist dashboard.
- OCR upload and correction card.
- Workflow status panel.
- Safety review panel.
- Source grounding panel.
- Knowledge base context panel.
- Counseling draft with draft-only label.
- Static evaluation summary page.

Avoid screenshots with:

- real patient names
- phone numbers
- clinic names
- IDs
- addresses
- real prescription images
- claims of production or clinical validation
