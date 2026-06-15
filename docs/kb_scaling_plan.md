# Knowledge Base Scaling Plan

PharmaGuard AI currently uses local Markdown profiles as a controlled MVP knowledge base. Phase 1.8 adds governance scaffolding so the project can later scale beyond a small manual folder without weakening safety controls.

## Current Position

- The current drug profiles are draft educational placeholders.
- The profiles are not clinically validated.
- Pharmacist review is required for every generated output.
- `data/drug_profiles/drug_registry.json` is the source of truth for supported generic names, aliases, review status, source status, and RAG enablement.

## Future Ingestion Strategy

Future ingestion should use trusted sources only after review. Imported records must preserve provenance, source version, import date, reviewer, and status history. No profile should be automatically approved for patient-facing use.

The ingestion pipeline should:

1. Normalize explicit generic and brand identities.
2. Create a disabled draft profile.
3. Validate required metadata and required Markdown sections.
4. Route the draft to pharmacist review.
5. Enable RAG only after an explicit approval decision.
6. Preserve rejection reasons and source notes for auditability.

## Identity Resolution

The registry should resolve only explicit medication names and supported aliases. It must not infer a drug from conditions or broad classes such as antibiotic, painkiller, or antihistamine.

Future work can add stronger generic/brand identity resolution and a drug knowledge graph, but the same conservative rule should remain: vague text should not map to arbitrary medication profiles.

## Versioning And Provenance

At larger scale, each profile should track:

- Source document identifiers
- Source publication or revision dates
- Import date
- Review date
- Reviewer identity or role
- Approval status
- Superseded profile versions

## Future Knowledge Graph

A later knowledge graph can model relationships between ingredients, brands, classes, contraindication review concepts, and counseling topics. That graph should support pharmacist review workflows and citation-backed retrieval, not autonomous clinical decisions.

## Deferred Work

Dense retrieval remains deferred until the TF-IDF baseline, registry validation, and evaluation coverage are strong enough to compare against. OCR remains Phase 2 and should be added only after the local KB and RAG guardrails are stable.
