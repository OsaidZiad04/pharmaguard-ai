# AI Development Protocol

This protocol guides future Codex-assisted development for PharmaGuard AI.

## Phase Execution

- Execute work in small, named phases.
- Keep each phase realistic, reviewable, and independently verifiable.
- Preserve existing behavior unless the phase explicitly requires a change.
- Do not start a new implementation phase during a documentation or cleanup task.
- Avoid risky integrations late in a session; defer them to a new explicit phase with tests and rollback clarity.

## Prompt Structure

Future Codex prompts should include:

- Current project state.
- Phase name and goal.
- Explicit non-goals.
- Safety and privacy constraints.
- Files or modules likely affected.
- Acceptance criteria.
- Required verification commands.
- Expected handoff format.

## Safety And Privacy Rules

- Preserve pharmacist-in-the-loop control.
- Keep generated outputs draft-only.
- Do not create final medical advice.
- Do not use real patient data.
- Do not commit real prescription images.
- Do not call external medical or OCR APIs unless a future phase explicitly authorizes it.
- Treat OCR output as unverified until pharmacist correction.
- Keep possible identifiers framed as possible identifiers, not confirmed PII.
- Maintain insufficient-context behavior for unknown or weak-context cases.

## Verification Rules

- Run relevant verification commands for every implementation phase.
- For backend behavior changes, run `cd backend && python -m pytest`.
- For RAG changes, run `cd backend && python scripts/evaluate_rag.py`.
- For KB changes, run `cd backend && python scripts/kb_report.py`.
- For OCR changes, run `cd backend && python scripts/evaluate_ocr.py`.
- For frontend changes, run `cd frontend && npm run typecheck` and `cd frontend && npm run build`.
- For documentation-only changes, `git status` and `git diff --check` are usually sufficient.

## Documentation Rules

- Update `docs/PROJECT_STATE.md` after every future phase.
- Link new major documents from `README.md` or the relevant docs index when useful.
- Keep roadmap status aligned with implemented phases.
- Document new safety or privacy implications before handoff.

## Handoff Rules

Every future handoff should summarize:

- Phase name.
- Files created.
- Files modified.
- Tests and evaluation commands run.
- Evaluation results.
- Safety and privacy impact.
- Remaining limitations.
- Recommended next step.
