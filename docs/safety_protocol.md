# Safety Protocol

PharmaGuard AI supports pharmacists only. It does not replace professional judgment, clinical guidelines, legal requirements, or local pharmacy policy.

## Non-Negotiable Guardrails

- Never present AI output as a final medical decision.
- Require pharmacist confirmation before generating patient-facing counseling drafts.
- Treat low confidence extraction as review-required.
- Do not guess unknown medication names.
- Warn when patient context is missing:
  - age
  - pregnancy status
  - allergies
  - current medications

## Current Scaffold Behavior

The backend safety service always sets pharmacist review as required. The UI displays draft-only wording and separates extraction, drug information, safety alerts, and counseling note output.

## Unsafe Output Avoidance

The system should avoid:

- final dosing recommendations
- diagnosis
- treatment selection
- drug substitution decisions
- claims that a medication is appropriate for a specific patient
- hidden assumptions about allergies, pregnancy, age, renal function, or drug interactions

## Human Control

The pharmacist must verify:

- prescription text accuracy
- medication identity
- dose, route, frequency, and duration
- patient-specific risk factors
- counseling note correctness
- whether the output is appropriate to share

## TODO

- Add source citations for every RAG-supported statement.
- Add structured pharmacist sign-off metadata.
- Add evaluation checks for unsafe claims.
- Add logging that excludes protected health information.
