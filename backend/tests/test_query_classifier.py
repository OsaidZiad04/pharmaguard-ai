from app.rag.query_classifier import classify_query


def test_query_classifier_identifies_drug_lookup() -> None:
    result = classify_query("paracetamol overview information")

    assert result.query_type == "drug_lookup"
    assert result.detected_medication_terms == ["paracetamol"]
    assert result.risk_level == "low"
    assert result.pharmacist_review_required is True


def test_query_classifier_identifies_counseling_request() -> None:
    result = classify_query("ibuprofen counseling points for pharmacist review")

    assert result.query_type == "counseling_request"
    assert result.detected_medication_terms == ["ibuprofen"]
    assert result.risk_level == "medium"


def test_query_classifier_identifies_safety_check() -> None:
    result = classify_query("amoxicillin allergy safety warning")

    assert result.query_type == "safety_check"
    assert result.detected_medication_terms == ["amoxicillin"]
    assert result.risk_level == "medium"


def test_query_classifier_identifies_dose_frequency_check() -> None:
    result = classify_query("metformin exact dose and frequency check")

    assert result.query_type == "dose_frequency_check"
    assert result.missing_fields_requested == ["dose", "frequency"]
    assert result.risk_level == "high"


def test_query_classifier_identifies_multiple_medication_review() -> None:
    result = classify_query("review paracetamol and ibuprofen together")

    assert result.query_type == "multiple_medication_review"
    assert result.detected_medication_terms == ["ibuprofen", "paracetamol"]
    assert result.risk_level == "high"


def test_query_classifier_identifies_unknown_and_ambiguous_queries() -> None:
    unknown = classify_query("xyzmed 20 mg counseling")
    ambiguous = classify_query("general counseling options")

    assert unknown.query_type == "unsupported_or_unknown"
    assert unknown.risk_level == "high"
    assert ambiguous.query_type == "general_or_ambiguous"
    assert ambiguous.detected_medication_terms == []
