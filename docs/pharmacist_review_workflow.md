# Pharmacist Review Workflow

Phase 3B-C adds a design plan for future pharmacist review workflow. It does not implement production sign-off, does not approve current profiles, and does not enable patient-facing output.

## Review Status Path

Future profile promotion path:

`draft -> pending_review -> reviewed`

Rejected or unsafe profiles should move to `rejected` or be disabled for RAG.

## Review Checklist

A future pharmacist review should verify:

- medication identity and aliases
- source references and provenance
- section completeness
- unsupported or ambiguous statements
- counseling draft wording
- safety notes and referral prompts
- absence of final medical advice
- patient-facing policy status
- update/review date requirements

## Required Registry Metadata

Before a profile can be treated as reviewed, it must include:

- non-empty `source_refs`
- valid source category
- `last_reviewed_at`
- `reviewed_by_role`
- `review_status: reviewed`
- `clinical_validation_status: pharmacist_reviewed`
- review notes

Current profiles do not meet these requirements.

## Pharmacist Review Records

Future production review records should capture:

- reviewer role, not personal patient data
- timestamp
- source package/version
- decision: approve, request changes, reject, disable
- notes on limitations

This project does not yet include a production audit database. Synthetic workflow traces are engineering artifacts only.

## Output Policy

Even after pharmacist review, generated counseling should remain draft support unless a future governance policy explicitly enables patient-facing output under production controls. The current policy keeps `patient_facing_allowed: false` for all profiles.
