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


def test_drug_lookup_returns_governance_metadata_for_rag_sources() -> None:
    result = lookup_drug_card("paracetamol")

    assert result.found is True
    assert result.retrieved_chunks
    assert result.retrieved_chunks[0].source_status == "placeholder_educational"
    assert result.retrieved_chunks[0].review_status == "draft"
    assert result.retrieved_chunks[0].clinical_validation_status == "not_validated"
    assert result.retrieved_chunks[0].requires_pharmacist_review is True
    assert result.retrieved_chunks[0].patient_facing_allowed is False
