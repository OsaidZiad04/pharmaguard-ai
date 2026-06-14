from app.services.safety_service import assess_prescription_analysis


def test_safety_service_flags_low_confidence() -> None:
    assessment = assess_prescription_analysis(
        extracted_medications=[
            {
                "name": "paracetamol",
                "confidence": 0.4,
                "is_known": True,
            }
        ],
        confidence_score=0.4,
        patient_context=None,
    )

    codes = {alert.code for alert in assessment.safety_alerts}
    assert "LOW_CONFIDENCE_REVIEW" in codes
    assert assessment.pharmacist_review_required is True
