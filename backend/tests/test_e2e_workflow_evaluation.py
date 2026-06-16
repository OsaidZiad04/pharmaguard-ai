from app.workflows.e2e_evaluation import (
    evaluate_e2e_workflow_case,
    load_e2e_workflow_cases,
    run_e2e_workflow_evaluation,
)


def _case(case_id: str) -> dict:
    return next(case for case in load_e2e_workflow_cases() if case["case_id"] == case_id)


def test_e2e_workflow_cases_load_required_scenarios() -> None:
    cases = load_e2e_workflow_cases()
    case_ids = {case["case_id"] for case in cases}

    assert len(cases) >= 10
    assert "E2E-OCR-RAG-001" in case_ids
    assert "E2E-OCR-RAG-002" in case_ids
    assert "E2E-OCR-RAG-005" in case_ids
    assert "E2E-OCR-RAG-010" in case_ids
    assert any(case["input_mode"] == "fixture_ocr" for case in cases)


def test_e2e_runner_passes_current_synthetic_baseline() -> None:
    report = run_e2e_workflow_evaluation()

    assert report["total_cases"] >= 10
    assert report["failed_cases"] == 0
    assert report["privacy_warning_summary"]["failed"] == 0
    assert report["rag_source_grounding_summary"]["failed"] == 0
    assert report["pharmacist_review_required_summary"]["failed"] == 0
    assert all(case_result["trace"]["trace_id"] for case_result in report["case_results"])


def test_clean_supported_medication_retrieves_source_backed_context() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-001"))

    assert result["passed"] is True
    assert result["extracted_medications"] == ["paracetamol"]
    assert "paracetamol.md" in result["retrieved_sources"]
    assert result["counseling_status"]["available"] is True


def test_noisy_ocr_requires_corrected_text_for_downstream_analysis() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-002"))

    assert result["passed"] is True
    assert "paracetamol" not in result["unverified_ocr_extracted_medications"]
    assert result["extracted_medications"] == ["paracetamol"]
    assert result["checks"]["correction_boundary_enforced"] is True
    assert result["checks"]["unverified_ocr_not_used_downstream"] is True


def test_unknown_medication_produces_insufficient_context() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-005"))

    assert result["passed"] is True
    assert result["extracted_medications"] == []
    assert result["unsupported_medications_found"] == ["xyzmed"]
    assert result["insufficient_context"] is True
    assert result["counseling_status"]["available"] is False


def test_privacy_warnings_remain_possible_identifier_warnings() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-006"))

    assert result["passed"] is True
    assert result["privacy_warning_status"]["detected"] == [
        "phone_number_like",
        "patient_name_label",
    ]
    assert result["privacy_warning_status"]["passed"] is True


def test_exact_dose_and_final_advice_cases_remain_draft_only() -> None:
    for case_id in ["E2E-OCR-RAG-008", "E2E-OCR-RAG-009"]:
        result = evaluate_e2e_workflow_case(_case(case_id))

        assert result["passed"] is True
        assert result["checks"]["final_advice_language_absent"] is True
        assert result["checks"]["must_not_include_terms_absent"] is True
        assert result["pharmacist_review_required_status"]["passed"] is True


def test_fixture_backed_case_uses_synthetic_provider_text() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-010"))

    assert result["passed"] is True
    assert result["input_mode"] == "fixture_ocr"
    assert result["extracted_medications"] == ["ibuprofen", "paracetamol"]
    assert {"ibuprofen.md", "paracetamol.md"}.issubset(
        set(result["retrieved_sources"])
    )
