# Knowledge Base Governance

Phase 3A upgrades the local Markdown drug knowledge base with explicit governance metadata. This is an engineering safety layer, not clinical validation.

## Current Status

The current knowledge base contains 15 local Markdown profiles. Every current profile is:

- `source_status: placeholder_educational`
- `review_status: draft`
- `clinical_validation_status: not_validated`
- `requires_pharmacist_review: true`
- `patient_facing_allowed: false`
- `counseling_draft_allowed: true`

The profiles remain enabled for prototype RAG so the system can be tested, but their outputs must stay pharmacist-support drafts.

## Registry Governance Fields

`data/drug_profiles/drug_registry.json` includes governance fields for each profile:

- `profile_id`
- `canonical_name`
- `source_status`
- `review_status`
- `clinical_validation_status`
- `requires_pharmacist_review`
- `patient_facing_allowed`
- `counseling_draft_allowed`
- `source_refs`
- `last_reviewed_at`
- `reviewed_by_role`
- `notes`

Current profiles intentionally have empty `source_refs`, no reviewer, and no review date because no trusted clinical source package has been ingested or pharmacist-reviewed.

## Source Catalog

`data/drug_profiles/source_catalog.json` defines source categories and governance requirements:

- `regulatory_label`
- `official_drug_monograph`
- `national_formulary`
- `peer_reviewed_reference`
- `local_placeholder`

`local_placeholder` is the only category represented by the current content. It is suitable for engineering demos and prototype RAG only. It is not allowed for clinical use.

## Governance Validation

`backend/app/kb/governance.py` validates:

- required governance metadata
- review/source/clinical validation status values
- patient-facing output restrictions
- pharmacist review requirements
- source reference requirements for trusted-source-ready profiles
- alias conflicts through the registry
- draft and placeholder warnings

Blocking examples:

- `patient_facing_allowed: true` without pharmacist-reviewed clinical validation
- `clinical_validation_status: pharmacist_reviewed` without reviewer role and review date
- trusted-source-ready status without source references
- duplicate aliases across enabled drugs

Warnings are expected for current profiles because they are draft placeholder content enabled for engineering RAG.

## Governance Report

Run from `backend/`:

```bash
python scripts/kb_governance_report.py
```

The report prints profile counts, status summaries, source catalog categories, blockers, and warnings. A passing governance report means the registry follows project safety rules. It does not mean the drug content is clinically validated.

## RAG Metadata

Retrieved chunks now include governance metadata where available:

- `source_status`
- `review_status`
- `clinical_validation_status`
- `requires_pharmacist_review`
- `patient_facing_allowed`
- `counseling_draft_allowed`

The metadata helps the dashboard and API consumers show that current RAG context is draft, placeholder, and not patient-facing.

## Retrieval Diagnostics And Safety Rules

Phase 3B-C uses governance metadata in retrieval diagnostics and safety-rule findings. Placeholder-only or not-clinically-validated retrieved context produces pharmacist-review warnings and patient-facing output remains blocked.

These checks do not promote a profile and do not validate clinical content. They only make the current governance limits explicit in workflow outputs and reports.

## Requirements Before Clinical Use

Before any profile could be treated as clinically reliable, the project would need:

- trusted source references with provenance
- pharmacist review workflow
- reviewer role and review timestamp
- source versioning
- safety evaluation beyond synthetic tests
- production privacy and audit controls
- formal clinical governance outside this prototype

Until then, all outputs remain pharmacist-support drafts only.

## Final Packaging Note

Phase 4-Final includes KB governance status in final reports, the static evaluation page, and portfolio documentation. This improves project communication only. It does not mark any profile as reviewed, clinically validated, trusted-source-ready, or patient-facing.
