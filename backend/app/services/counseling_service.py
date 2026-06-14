from app.schemas.counseling import CounselingRequest, CounselingResponse
from app.services.rag_service import build_grounded_counseling_note
from app.services.safety_service import (
    assess_counseling_generation,
    build_missing_knowledge_base_context_alert,
)


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
    counseling_note, retrieved_sources, insufficient_context = build_grounded_counseling_note(
        medication_name=medication.name,
        strength=medication.strength,
        directions=medication.directions,
        additional_notes=payload.additional_notes,
    )

    if insufficient_context:
        alerts.append(build_missing_knowledge_base_context_alert(medication.name))

    return CounselingResponse(
        counseling_note=counseling_note,
        safety_alerts=alerts,
        retrieved_sources=retrieved_sources,
        insufficient_context=insufficient_context,
        pharmacist_review_required=True,
    )
