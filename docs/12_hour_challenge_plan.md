# 12-Hour Challenge Plan

## Goal

Build a portfolio-ready scaffold that demonstrates clear architecture, safety thinking, and a working pharmacist dashboard without pretending to be a complete medical system.

## Hour 1: Repository Foundation

- Create folders and baseline docs.
- Add `.gitignore`, `.env.example`, and README files.

## Hour 2: FastAPI Skeleton

- Add app factory basics.
- Configure CORS.
- Add `/health`.

## Hour 3: Schemas and Services

- Add prescription, drug, counseling, and safety schemas.
- Add placeholder extraction and safety services.

## Hour 4: Mock Drug Lookup

- Create local mock drug index.
- Add `/drugs/{drug_name}`.
- Add unknown-medication safety behavior.

## Hour 5: Counseling Placeholder

- Add pharmacist-confirmed counseling generation endpoint.
- Keep outputs explicitly draft-only.

## Hour 6: RAG Module Skeletons

- Add chunker, embedder, vector store, retriever, generator, and prompt templates.
- Mark future work with TODO comments.

## Hour 7: Backend Tests

- Test health endpoint.
- Test extraction candidates.
- Test low-confidence safety behavior.
- Test unknown medication lookup.

## Hour 8: Next.js Setup

- Add Tailwind configuration.
- Add shared TypeScript interfaces and API client.

## Hour 9: Dashboard Layout

- Build header, workflow stepper, prescription intake, and review panels.
- Use a clean pharmacy-desk visual style.

## Hour 10: API Flow

- Connect prescription analysis.
- Connect drug lookup.
- Connect counseling generation after pharmacist confirmation.

## Hour 11: Documentation Pass

- Finalize architecture, safety, data privacy, and roadmap docs.

## Hour 12: Verification and Polish

- Run pytest.
- Run frontend build or dev server.
- Fix obvious layout, type, or API issues.
