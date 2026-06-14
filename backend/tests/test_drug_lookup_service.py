from app.services.drug_lookup_service import lookup_drug_card


def test_drug_lookup_handles_unknown_medication_safely() -> None:
    result = lookup_drug_card("Xyzmed")

    assert result.found is False
    assert result.drug is None
    assert any(
        alert.code == "UNKNOWN_MEDICATION_DO_NOT_GUESS"
        for alert in result.safety_alerts
    )
    assert result.pharmacist_review_required is True
