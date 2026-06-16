# Medication Safety Rules

Phase 3C adds deterministic medication safety rules for pharmacist workflow support. This is not a clinical decision engine, drug-drug interaction checker, contraindication checker, or patient-specific recommendation system.

## Scope

Added backend modules:

- `backend/app/safety/safety_models.py`
- `backend/app/safety/medication_rules.py`
- `backend/scripts/safety_rules_report.py`

Prescription analysis responses now include additive `safety_findings` metadata. Existing safety alerts remain in place.

## Supported Rule Findings

Current deterministic rules include:

- `missing_dose`
- `missing_frequency`
- `missing_duration`
- `missing_route`
- `multiple_medications_detected`
- `unsupported_medication_detected`
- `no_medication_detected`
- `possible_identifier_detected`
- `placeholder_kb_only`
- `not_clinically_validated`
- `pharmacist_review_required`
- `patient_facing_not_allowed`
- `duplicate_medication_mention`
- `ambiguous_strength_or_units`
- `source_grounding_required`
- `interaction_check_unavailable`
- `contraindication_check_unavailable`

Each finding includes:

- `rule_id`
- severity: `info`, `caution`, `warning`, or `blocker`
- message
- detected terms
- pharmacist action
- evidence source
- `patient_facing_allowed: false`

## Explicitly Not Supported

The system does not perform:

- real drug-drug interaction validation
- contraindication validation
- diagnosis
- treatment selection
- patient-specific dose recommendation
- clinical appropriateness decisions

The safety analysis marks:

- `interaction_check_available: false`
- `contraindication_check_available: false`
- `requires_trusted_source_ingestion: true`

## Safety Rules Report

Run from `backend/`:

```bash
python scripts/safety_rules_report.py
```

The report runs synthetic examples for missing fields, unsupported medication text, no medication, possible identifier warnings, placeholder KB context, and not-clinically-validated profiles.

This is an engineering safety support report, not clinical validation.

## Pharmacist Boundary

All safety findings are prompts for pharmacist review. They must not be presented as final medical advice or as proof that a prescription is clinically appropriate.

Phase 4-Final surfaces safety-rule evidence in reports and demo materials only. It does not add new clinical rules and does not change patient-facing restrictions.
