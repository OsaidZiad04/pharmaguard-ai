from app.schemas.counseling import CounselingRequest, CounselingResponse
from app.services.safety_service import assess_counseling_generation


def generate_counseling_note(payload: CounselingRequest) -> CounselingResponse:
    alerts = assess_counseling_generation(
        pharmacist_confirmed=payload.medication.pharmacist_confirmed,
        patient_context_confirmed=payload.patient_context_confirmed,
    )

    if not payload.medication.pharmacist_confirmed:
        return CounselingResponse(
            counseling_note=(
                "Counseling draft blocked. A pharmacist must confirm the medication "
                "name, strength, and directions before a patient-facing draft is created."
            ),
            safety_alerts=alerts,
            pharmacist_review_required=True,
        )

    medication = payload.medication
    strength = medication.strength or "strength not confirmed"
    directions = medication.directions or "directions not confirmed"
    additional = (
        f" Pharmacist note: {payload.additional_notes.strip()}"
        if payload.additional_notes
        else ""
    )

    note = (
        "Draft counseling note for pharmacist review: "
        f"{medication.name} ({strength}). Confirmed directions: {directions}. "
        "Verify patient-specific factors, including age, pregnancy status, allergies, "
        "and current medications, before sharing any counseling. "
        "This draft is not a final medical decision and must be reviewed by the pharmacist."
        f"{additional}"
    )

    return CounselingResponse(
        counseling_note=note,
        safety_alerts=alerts,
        pharmacist_review_required=True,
    )
