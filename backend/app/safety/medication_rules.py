from __future__ import annotations

import re
from typing import Any

from app.kb.registry import get_drug_registry, normalize_drug_term
from app.ocr.providers import detect_possible_identifiers
from app.safety.safety_models import MedicationSafetyAnalysis, MedicationSafetyRuleResult


FREQUENCY_PATTERN = re.compile(
    r"\b(?:every|daily|once|twice|three times|four times|q\d+h|bid|tid|qid|as needed|prn)\b",
    flags=re.IGNORECASE,
)
DURATION_PATTERN = re.compile(
    r"\b(?:for\s+\d+\s+(?:day|days|week|weeks|month|months)|duration|course)\b",
    flags=re.IGNORECASE,
)
ROUTE_PATTERN = re.compile(
    r"\b(?:oral|orally|by mouth|po|take|apply|topical|inject|inhaler|inhale|eye|ear|nasal|sublingual)\b",
    flags=re.IGNORECASE,
)
AMBIGUOUS_STRENGTH_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|%)?\b")
MEDICATION_WITH_STRENGTH_PATTERN = re.compile(
    r"\b([a-z][a-z0-9-]{3,})\s+\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|%)\b",
    flags=re.IGNORECASE,
)
MEDICATION_LABEL_PATTERN = re.compile(
    r"\b(?:medication|drug|medicine|rx)\s*:\s*([a-z][a-z0-9-]{3,})",
    flags=re.IGNORECASE,
)


def analyze_medication_safety_rules(
    prescription_text: str,
    extracted_medications: list[Any] | None = None,
    retrieved_chunks: list[Any] | None = None,
    detected_possible_identifiers: list[str] | None = None,
) -> MedicationSafetyAnalysis:
    extracted_medications = extracted_medications or []
    retrieved_chunks = retrieved_chunks or []
    findings: list[MedicationSafetyRuleResult] = []

    supported_names = [_medication_field(medication, "name") for medication in extracted_medications]
    unknown_terms = _detect_unsupported_medication_terms(
        prescription_text,
        known_medications=supported_names,
    )

    if not extracted_medications and not unknown_terms:
        findings.append(
            _finding(
                "no_medication_detected",
                "blocker",
                "No supported medication term was detected in the provided text.",
                [],
                "Verify the prescription text and enter a confirmed medication before analysis.",
                "prescription_text",
            )
        )

    if unknown_terms:
        findings.append(
            _finding(
                "unsupported_medication_detected",
                "blocker",
                "Medication-like terms were detected but are not supported by the local KB.",
                unknown_terms,
                "Do not guess. Verify the medication identity and local knowledge-base coverage.",
                "prescription_text",
            )
        )

    for medication in extracted_medications:
        name = _medication_field(medication, "name")
        source_text = _medication_field(medication, "source_text") or prescription_text
        strength = _medication_field(medication, "strength")
        directions = _medication_field(medication, "directions")
        combined_text = f"{source_text} {directions}".strip()

        if not strength:
            findings.append(
                _finding(
                    "missing_dose",
                    "caution",
                    "Medication strength or dose was not detected.",
                    [name] if name else [],
                    "Confirm the dose or strength from the prescription before counseling.",
                    "prescription_text",
                )
            )

        if not directions or not FREQUENCY_PATTERN.search(combined_text):
            findings.append(
                _finding(
                    "missing_frequency",
                    "caution",
                    "Frequency was not clearly detected from the prescription text.",
                    [name] if name else [],
                    "Confirm frequency with the prescription and pharmacist review.",
                    "prescription_text",
                )
            )

        if not DURATION_PATTERN.search(combined_text):
            findings.append(
                _finding(
                    "missing_duration",
                    "info",
                    "Duration was not clearly detected from the prescription text.",
                    [name] if name else [],
                    "Check whether duration is required for this prescription context.",
                    "prescription_text",
                )
            )

        if not ROUTE_PATTERN.search(combined_text):
            findings.append(
                _finding(
                    "missing_route",
                    "caution",
                    "Route was not clearly detected from the prescription text.",
                    [name] if name else [],
                    "Confirm route before patient counseling.",
                    "prescription_text",
                )
            )

    if len(extracted_medications) > 1:
        findings.append(
            _finding(
                "multiple_medications_detected",
                "caution",
                "Multiple supported medications were detected.",
                supported_names,
                "Review each medication separately and do not infer interactions.",
                "prescription_text",
            )
        )

    duplicate_terms = _duplicate_terms(supported_names)
    if duplicate_terms:
        findings.append(
            _finding(
                "duplicate_medication_mention",
                "caution",
                "Duplicate medication mentions were detected.",
                duplicate_terms,
                "Confirm whether duplicate mentions are intentional or repeated text.",
                "prescription_text",
            )
        )

    if _ambiguous_strength_without_unit(prescription_text):
        findings.append(
            _finding(
                "ambiguous_strength_or_units",
                "caution",
                "A numeric medication-like value may be missing a clear unit.",
                [],
                "Confirm strength and units before review or counseling.",
                "prescription_text",
            )
        )

    identifiers = detected_possible_identifiers
    if identifiers is None:
        identifiers = detect_possible_identifiers(prescription_text)
    if identifiers:
        findings.append(
            _finding(
                "possible_identifier_detected",
                "warning",
                "Possible identifier-like patterns were detected.",
                identifiers,
                "Treat as possible identifiers and avoid storing real patient data.",
                "prescription_text",
            )
        )

    findings.extend(_retrieval_governance_findings(retrieved_chunks))
    findings.extend(_system_policy_findings())

    return MedicationSafetyAnalysis(
        findings=_dedupe_findings(findings),
        pharmacist_review_required=True,
        patient_facing_allowed=False,
        interaction_check_available=False,
        contraindication_check_available=False,
        requires_trusted_source_ingestion=True,
    )


def _retrieval_governance_findings(
    retrieved_chunks: list[Any],
) -> list[MedicationSafetyRuleResult]:
    if not retrieved_chunks:
        return [
            _finding(
                "source_grounding_required",
                "warning",
                "Medication-specific support requires retrieved source context.",
                [],
                "Retrieve source-grounded KB context or return insufficient context.",
                "retrieval_metadata",
            )
        ]

    findings: list[MedicationSafetyRuleResult] = []
    source_statuses = {_field(chunk, "source_status") for chunk in retrieved_chunks}
    validation_statuses = {
        _field(chunk, "clinical_validation_status") for chunk in retrieved_chunks
    }

    if source_statuses == {"placeholder_educational"}:
        findings.append(
            _finding(
                "placeholder_kb_only",
                "warning",
                "Retrieved KB context is placeholder educational material only.",
                sorted(source_statuses),
                "Keep output draft-only and verify against trusted pharmacist-reviewed sources.",
                "kb_governance",
            )
        )

    if validation_statuses.intersection({"", "not_validated", "engineering_only"}):
        findings.append(
            _finding(
                "not_clinically_validated",
                "warning",
                "Retrieved KB context is not clinically validated.",
                sorted(status for status in validation_statuses if status),
                "Do not treat local RAG output as clinical validation.",
                "kb_governance",
            )
        )

    if not all(_bool_field(chunk, "patient_facing_allowed") for chunk in retrieved_chunks):
        findings.append(
            _finding(
                "patient_facing_not_allowed",
                "blocker",
                "Current KB governance does not allow patient-facing output.",
                [],
                "Keep generated content as pharmacist-support draft only.",
                "kb_governance",
            )
        )

    if any(_bool_field(chunk, "requires_pharmacist_review") for chunk in retrieved_chunks):
        findings.append(
            _finding(
                "pharmacist_review_required",
                "info",
                "Retrieved KB context requires pharmacist review.",
                [],
                "Pharmacist must review before any patient-facing use.",
                "kb_governance",
            )
        )

    return findings


def _system_policy_findings() -> list[MedicationSafetyRuleResult]:
    return [
        _finding(
            "pharmacist_review_required",
            "info",
            "Pharmacist review is mandatory for all medication-support output.",
            [],
            "Review and approve any draft before use.",
            "system_policy",
        ),
        _finding(
            "interaction_check_unavailable",
            "info",
            "Drug-drug interaction checking is not available in this prototype.",
            [],
            "Use validated professional references and pharmacist judgment for interactions.",
            "system_policy",
        ),
        _finding(
            "contraindication_check_unavailable",
            "info",
            "Contraindication checking is not available in this prototype.",
            [],
            "Use validated professional references and pharmacist judgment for contraindications.",
            "system_policy",
        ),
    ]


def _detect_unsupported_medication_terms(
    text: str,
    known_medications: list[str],
) -> list[str]:
    supported_terms = _supported_terms()
    known_terms = {normalize_drug_term(value) for value in known_medications if value}
    unsupported: set[str] = set()

    for pattern in (MEDICATION_LABEL_PATTERN, MEDICATION_WITH_STRENGTH_PATTERN):
        for match in pattern.finditer(text):
            term = normalize_drug_term(match.group(1))
            if not term or term in supported_terms or term in known_terms:
                continue
            if term in {"take", "apply", "directions", "review", "tablet"}:
                continue
            unsupported.add(term)
    return sorted(unsupported)


def _supported_terms() -> set[str]:
    try:
        registry = get_drug_registry()
    except (FileNotFoundError, ValueError):
        return set()

    terms: set[str] = set()
    for entry in registry.list_enabled_drugs():
        terms.add(normalize_drug_term(entry.generic_name))
        for alias in entry.aliases:
            terms.add(normalize_drug_term(alias))
    return terms


def _medication_field(medication: Any, field_name: str) -> str:
    value = getattr(medication, field_name, None)
    if value is None and isinstance(medication, dict):
        value = medication.get(field_name)
    return str(value).strip() if value is not None else ""


def _field(chunk: Any, field_name: str) -> str:
    value = getattr(chunk, field_name, None)
    if value is None and isinstance(chunk, dict):
        value = chunk.get(field_name)
    return str(value).strip() if value is not None else ""


def _bool_field(chunk: Any, field_name: str) -> bool:
    value = getattr(chunk, field_name, None)
    if value is None and isinstance(chunk, dict):
        value = chunk.get(field_name)
    return bool(value)


def _duplicate_terms(values: list[str]) -> list[str]:
    seen = set()
    duplicates = set()
    for value in values:
        if not value:
            continue
        normalized = normalize_drug_term(value)
        if normalized in seen:
            duplicates.add(normalized)
        seen.add(normalized)
    return sorted(duplicates)


def _ambiguous_strength_without_unit(text: str) -> bool:
    for match in AMBIGUOUS_STRENGTH_PATTERN.finditer(text):
        token = match.group(0)
        if re.search(r"(?:mg|mcg|g|ml|%)", token, flags=re.IGNORECASE):
            continue
        if int(float(re.findall(r"\d+(?:\.\d+)?", token)[0])) >= 10:
            return True
    return False


def _finding(
    rule_id: str,
    severity: str,
    message: str,
    detected_terms: list[str],
    pharmacist_action: str,
    evidence_source: str,
) -> MedicationSafetyRuleResult:
    return MedicationSafetyRuleResult(
        rule_id=rule_id,
        severity=severity,
        message=message,
        detected_terms=detected_terms,
        pharmacist_action=pharmacist_action,
        evidence_source=evidence_source,
        patient_facing_allowed=False,
    )


def _dedupe_findings(
    findings: list[MedicationSafetyRuleResult],
) -> list[MedicationSafetyRuleResult]:
    deduped: dict[tuple[str, str], MedicationSafetyRuleResult] = {}
    for finding in findings:
        key = (finding.rule_id, ",".join(finding.detected_terms))
        deduped[key] = finding
    return list(deduped.values())
