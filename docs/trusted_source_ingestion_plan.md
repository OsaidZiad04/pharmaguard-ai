# Trusted Source Ingestion Plan

Phase 3B-C includes design-only planning for future trusted-source ingestion. No trusted clinical sources are ingested in this phase, and no current profile is promoted.

## Goals

Future ingestion should allow the knowledge base to move from placeholder educational content toward reviewed source-backed profiles while preserving provenance, pharmacist oversight, and patient-safety boundaries.

## Source Catalog Usage

`data/drug_profiles/source_catalog.json` defines source categories:

- `regulatory_label`
- `official_drug_monograph`
- `national_formulary`
- `peer_reviewed_reference`
- `local_placeholder`

Future ingestion must record source category, source reference, version/date where available, and review metadata before a profile can leave draft status.

## Ingestion Stages

1. Source candidate registration
   - Record source category and provenance.
   - Confirm licensing and privacy requirements.
   - Store reference metadata, not patient records.

2. Draft profile creation
   - Normalize generic and brand identity.
   - Create or update a draft profile.
   - Keep `patient_facing_allowed: false`.

3. Source mapping
   - Link each section to source references.
   - Preserve source version and retrieval date if applicable.
   - Flag unsupported or conflicting content for review.

4. Pharmacist review
   - Move profile to `pending_review`.
   - Require reviewer role and review timestamp.
   - Require review notes and source coverage checklist.

5. Promotion decision
   - Approved reviewed profiles can move to `reviewed`.
   - Rejected profiles remain disabled or draft with documented reason.
   - Patient-facing output remains disabled unless a future governance policy explicitly permits it.

## Required Metadata Before Review

- `source_refs`
- source category
- source notes
- `last_reviewed_at`
- `reviewed_by_role`
- `review_status`
- `clinical_validation_status`
- section-level provenance in a future schema

## Why No Profile Is Promoted Now

The current repository contains placeholder educational Markdown only. It does not include pharmacist-reviewed source evidence, source versioning, reviewer metadata, or clinical validation. Promoting profiles in this phase would overstate the project state.

## Future Impact

Future reviewed profiles could improve RAG source confidence and reduce governance warnings, but generated output should still remain pharmacist-support draft text until production governance, privacy, audit, and validation controls exist.
