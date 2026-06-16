# Portfolio Story

## Recruiter-Friendly Summary

PharmaGuard AI is a pharmacist-centered AI copilot prototype that demonstrates safe prescription intake, OCR correction, local RAG, knowledge-base governance, retrieval diagnostics, deterministic safety prompts, and evaluation-driven development.

It is built as a realistic healthcare AI portfolio project with strong safety boundaries rather than as a generic chatbot.

## Technical Depth

- FastAPI backend with modular services and schemas.
- Next.js TypeScript pharmacist dashboard.
- Local TF-IDF RAG over Markdown profiles.
- Knowledge-base registry and governance metadata.
- OCR provider abstraction with mock, synthetic, and disabled optional Tesseract adapter.
- Synthetic evaluation suites for RAG, OCR, E2E workflow, traceability, retrieval strategies, and safety rules.
- Deterministic workflow trace records.

## Product Thinking

The project focuses on pharmacist workflow control:

- OCR is assistive and unverified.
- Corrected text is the downstream boundary.
- RAG is source-grounded.
- Counseling is draft-only.
- Safety prompts guide pharmacist review.
- Patient-facing output is disabled.

## Safety And Governance

The project is explicit about what it does not do:

- no clinical validation
- no final medical advice
- no autonomous medical decisions
- no real patient data
- no external medical APIs
- no production OCR default

This makes the project credible because its limitations are engineered into the workflow instead of hidden.

## Strong Interview Angle

"I built PharmaGuard AI as an evaluation-driven healthcare AI prototype. The main challenge was not just building RAG or OCR, but designing the safety boundaries: pharmacist correction gates, KB governance, retrieval diagnostics, and deterministic rules that prevent the system from acting like a clinical decision engine."
