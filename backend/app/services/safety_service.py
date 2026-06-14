from dataclasses import dataclass
from typing import Any

from app.core.constants import (
    LOW_CONFIDENCE_THRESHOLD,
    REQUIRED_PATIENT_CONTEXT_FIELDS,
    SAFETY_BOUNDARY_MESSAGE,
)
from app.schemas.safety import SafetyAlert


@dataclass
class SafetyAssessment:
    missing_information: list[str]
    safety_alerts: list[SafetyAlert]
    pharmacist_review_required: bool = True


def assess_prescription_analysis(
    extracted_medications: list[dict],
    confidence_score: float,
    patient_context: Any | None,
) -> SafetyAssessment:
    """Apply scaffold safety rules to prescription analysis output."""
    missing_information = find_missing_patient_context(patient_context)
    alerts = [
        build_safety_boundary_alert(),
        build_pharmacist_review_alert(),
    ]

    if confidence_score < LOW_CONFIDENCE_THRESHOLD:
        alerts.append(build_low_confidence_alert(confidence_score))

    if not extracted_medications:
        alerts.append(build_unknown_medication_alert("unmatched prescription text"))

    for medication in extracted_medications:
        if medication.get("is_known") is False:
            alerts.append(build_unknown_medication_alert(medication.get("name", "unknown")))

    if missing_information:
        alerts.append(build_missing_context_alert(missing_information))

    return SafetyAssessment(
        missing_information=missing_information,
        safety_alerts=alerts,
        pharmacist_review_required=True,
    )


def assess_counseling_generation(
    pharmacist_confirmed: bool,
    patient_context_confirmed: bool,
) -> list[SafetyAlert]:
    alerts = [build_safety_boundary_alert(), build_pharmacist_review_alert()]

    if not pharmacist_confirmed:
        alerts.append(
            SafetyAlert(
                code="PHARMACIST_CONFIRMATION_MISSING",
                severity="critical",
                message=(
                    "Counseling draft generation is blocked until the pharmacist "
                    "confirms the medication details."
                ),
            )
        )

    if not patient_context_confirmed:
        alerts.append(
            SafetyAlert(
                code="PATIENT_CONTEXT_NOT_CONFIRMED",
                severity="warning",
                message=(
                    "Patient context has not been confirmed. Verify age, pregnancy "
                    "status, allergies, and current medications before patient counseling."
                ),
            )
        )

    return alerts


def find_missing_patient_context(patient_context: Any | None) -> list[str]:
    if patient_context is None:
        return list(REQUIRED_PATIENT_CONTEXT_FIELDS)

    missing: list[str] = []
    for field_name in REQUIRED_PATIENT_CONTEXT_FIELDS:
        value = getattr(patient_context, field_name, None)
        if value is None or value == "" or value == []:
            missing.append(field_name)
    return missing


def build_safety_boundary_alert() -> SafetyAlert:
    return SafetyAlert(
        code="NO_FINAL_MEDICAL_DECISION",
        severity="info",
        message=SAFETY_BOUNDARY_MESSAGE,
    )


def build_pharmacist_review_alert() -> SafetyAlert:
    return SafetyAlert(
        code="PHARMACIST_REVIEW_REQUIRED",
        severity="info",
        message="Pharmacist confirmation is required before any patient-facing use.",
    )


def build_low_confidence_alert(confidence_score: float) -> SafetyAlert:
    return SafetyAlert(
        code="LOW_CONFIDENCE_REVIEW",
        severity="warning",
        message=(
            f"Extraction confidence is {confidence_score:.2f}, below the "
            f"{LOW_CONFIDENCE_THRESHOLD:.2f} review threshold."
        ),
    )


def build_unknown_medication_alert(drug_name: str) -> SafetyAlert:
    return SafetyAlert(
        code="UNKNOWN_MEDICATION_DO_NOT_GUESS",
        severity="critical",
        message=(
            f"Medication '{drug_name}' was not found in the local mock index. "
            "Do not infer or guess medication details."
        ),
    )


def build_missing_knowledge_base_context_alert(drug_name: str) -> SafetyAlert:
    return SafetyAlert(
        code="INSUFFICIENT_KNOWLEDGE_BASE_CONTEXT",
        severity="warning",
        message=(
            f"Insufficient knowledge base context was retrieved for '{drug_name}'. "
            "Do not generate medication-specific content from unsupported assumptions."
        ),
    )


def build_missing_context_alert(missing_fields: list[str]) -> SafetyAlert:
    return SafetyAlert(
        code="MISSING_PATIENT_CONTEXT",
        severity="warning",
        message=(
            "Missing patient context: "
            + ", ".join(missing_fields)
            + ". Verify before counseling or clinical interpretation."
        ),
    )
