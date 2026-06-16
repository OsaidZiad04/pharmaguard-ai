from fastapi import APIRouter

from app.schemas.prescription import (
    ExtractedMedication,
    PrescriptionAnalysisResponse,
    PrescriptionTextRequest,
)
from app.safety.medication_rules import analyze_medication_safety_rules
from app.services.extraction_service import extract_medication_candidates
from app.services.safety_service import assess_prescription_analysis
from app.utils.confidence import aggregate_confidence

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.post("/analyze-text", response_model=PrescriptionAnalysisResponse)
def analyze_text(payload: PrescriptionTextRequest) -> PrescriptionAnalysisResponse:
    candidates = extract_medication_candidates(payload.raw_text)
    confidence_score = aggregate_confidence(
        [candidate["confidence"] for candidate in candidates]
    )
    safety_assessment = assess_prescription_analysis(
        extracted_medications=candidates,
        confidence_score=confidence_score,
        patient_context=payload.patient_context,
    )
    safety_rules = analyze_medication_safety_rules(
        prescription_text=payload.raw_text,
        extracted_medications=candidates,
    )

    return PrescriptionAnalysisResponse(
        extracted_medications=[
            ExtractedMedication(**candidate) for candidate in candidates
        ],
        confidence_score=confidence_score,
        missing_information=safety_assessment.missing_information,
        safety_alerts=safety_assessment.safety_alerts,
        safety_findings=safety_rules.findings,
        pharmacist_review_required=safety_assessment.pharmacist_review_required,
    )
