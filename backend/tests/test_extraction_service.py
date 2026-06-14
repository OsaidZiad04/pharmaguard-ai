from app.services.extraction_service import extract_medication_candidates


def test_extraction_service_returns_medication_candidates() -> None:
    result = extract_medication_candidates(
        "Rx: Paracetamol 500 mg tablets. Take 1 tablet every 6 hours as needed."
    )

    assert result
    assert result[0]["name"] == "paracetamol"
    assert result[0]["strength"] == "500 mg"
    assert result[0]["confidence"] > 0
