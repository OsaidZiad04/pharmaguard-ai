from app.rag.retriever import retrieve_contexts
from app.safety.medication_rules import analyze_medication_safety_rules
from app.services.extraction_service import extract_medication_candidates


def test_safety_rules_detect_missing_prescription_fields() -> None:
    text = "Medication: Ibuprofen. Directions: Take as directed."
    extracted = extract_medication_candidates(text)
    analysis = analyze_medication_safety_rules(text, extracted_medications=extracted)
    rule_ids = _rule_ids(analysis)

    assert "missing_dose" in rule_ids
    assert "missing_frequency" in rule_ids
    assert "missing_duration" in rule_ids
    assert analysis.pharmacist_review_required is True
    assert analysis.patient_facing_allowed is False


def test_safety_rules_detect_no_and_unsupported_medication() -> None:
    no_med = analyze_medication_safety_rules("Synthetic note only.")
    unsupported = analyze_medication_safety_rules("Medication: Xyzmed 20 mg.")

    assert "no_medication_detected" in _rule_ids(no_med)
    assert "unsupported_medication_detected" in _rule_ids(unsupported)
    assert all(finding.patient_facing_allowed is False for finding in unsupported.findings)


def test_safety_rules_detect_multiple_medications_and_identifiers() -> None:
    text = (
        "Patient: SYNTHETIC ONLY. Medication: Paracetamol 500 mg. "
        "Medication: Cetirizine 10 mg. Directions: Take daily for 2 days."
    )
    extracted = extract_medication_candidates(text)
    analysis = analyze_medication_safety_rules(text, extracted_medications=extracted)
    rule_ids = _rule_ids(analysis)

    assert "multiple_medications_detected" in rule_ids
    assert "possible_identifier_detected" in rule_ids


def test_safety_rules_detect_kb_governance_risks() -> None:
    text = "Medication: Paracetamol 500 mg. Directions: Take every 8 hours for 2 days."
    extracted = extract_medication_candidates(text)
    contexts = retrieve_contexts("paracetamol counseling", medication_name="paracetamol")
    analysis = analyze_medication_safety_rules(
        text,
        extracted_medications=extracted,
        retrieved_chunks=contexts,
    )
    rule_ids = _rule_ids(analysis)

    assert "placeholder_kb_only" in rule_ids
    assert "not_clinically_validated" in rule_ids
    assert "patient_facing_not_allowed" in rule_ids
    assert "pharmacist_review_required" in rule_ids


def test_safety_rules_mark_interactions_and_contraindications_unavailable() -> None:
    analysis = analyze_medication_safety_rules("Medication: Aspirin 100 mg.")
    rule_ids = _rule_ids(analysis)

    assert analysis.interaction_check_available is False
    assert analysis.contraindication_check_available is False
    assert analysis.requires_trusted_source_ingestion is True
    assert "interaction_check_unavailable" in rule_ids
    assert "contraindication_check_unavailable" in rule_ids


def test_safety_rules_do_not_create_final_medical_advice() -> None:
    analysis = analyze_medication_safety_rules("Medication: Amlodipine 5 mg.")
    forbidden = ["you should take", "take exactly", "final medical advice"]
    output = " ".join(
        f"{finding.message} {finding.pharmacist_action}" for finding in analysis.findings
    ).lower()

    assert all(term not in output for term in forbidden)


def _rule_ids(analysis) -> set[str]:
    return {finding.rule_id for finding in analysis.findings}
