import json

from app.workflows.e2e_evaluation import evaluate_e2e_workflow_case, load_e2e_workflow_cases


def _case(case_id: str) -> dict:
    return next(case for case in load_e2e_workflow_cases() if case["case_id"] == case_id)


def _step(trace: dict, step_name: str) -> dict:
    return next(step for step in trace["steps"] if step["step_name"] == step_name)


def _all_keys(value) -> set[str]:
    if isinstance(value, dict):
        keys = set(value.keys())
        for nested in value.values():
            keys.update(_all_keys(nested))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()


def test_trace_created_for_e2e_case_with_required_metadata() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-001"))
    trace = result["trace"]

    assert trace["trace_id"] == "trace-e2e-ocr-rag-001"
    assert trace["case_id"] == "E2E-OCR-RAG-001"
    assert trace["steps"]
    assert trace["synthetic_trace"] is True
    assert trace["contains_real_patient_data"] is False
    assert trace["stores_raw_image_bytes"] is False
    assert trace["pharmacist_review_required"] is True


def test_trace_marks_ocr_unverified_and_blocks_downstream_bypass() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-002"))
    trace = result["trace"]
    ocr_step = _step(trace, "ocr_extraction")
    bypass_step = _step(trace, "unverified_ocr_downstream_use")

    assert ocr_step["status"] == "completed"
    assert "OCR output is unverified." in ocr_step["safety_notes"]
    assert ocr_step["output_reference_type"] == "unverified_ocr_text_reference"
    assert bypass_step["status"] == "blocked"
    assert "not sent to prescription analysis" in bypass_step["summary"]


def test_trace_records_correction_gate_and_corrected_text_boundary() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-002"))
    trace = result["trace"]
    correction_step = _step(trace, "pharmacist_correction_gate")
    analysis_step = _step(trace, "prescription_analysis")

    assert correction_step["status"] == "completed"
    assert correction_step["output_reference_type"] == "pharmacist_corrected_text_reference"
    assert analysis_step["input_reference_type"] == "pharmacist_corrected_text_reference"
    assert trace["pharmacist_review_record"]["correction_completed"] is True
    assert trace["pharmacist_review_record"]["corrected_text_used_for_analysis"] is True


def test_trace_records_rag_sources_and_pharmacist_review_requirement() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-010"))
    trace = result["trace"]
    rag_step = _step(trace, "rag_retrieval")
    review_step = _step(trace, "pharmacist_review")

    assert rag_step["status"] == "completed"
    assert {"ibuprofen.md", "paracetamol.md"}.issubset(set(rag_step["source_refs"]))
    assert review_step["status"] == "completed"
    assert trace["pharmacist_review_required"] is True


def test_trace_does_not_store_raw_image_bytes_or_raw_text_payloads() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-006"))
    trace = result["trace"]
    serialized_trace = json.dumps(trace).lower()
    keys = _all_keys(trace)

    assert trace["stores_raw_image_bytes"] is False
    assert "raw_image_bytes" not in keys
    assert "ocr_text" not in keys
    assert "corrected_text" not in keys
    assert "555-010" not in serialized_trace
    assert "synthetic example" not in serialized_trace


def test_trace_marks_unsafe_unknown_medication_flow_as_blocked() -> None:
    result = evaluate_e2e_workflow_case(_case("E2E-OCR-RAG-005"))
    trace = result["trace"]

    assert trace["final_status"] == "blocked"
    assert _step(trace, "rag_retrieval")["status"] == "blocked"
    assert _step(trace, "counseling_generation")["status"] == "blocked"
    assert any(
        flag["code"] == "INSUFFICIENT_KNOWLEDGE_BASE_CONTEXT"
        for flag in trace["safety_flags"]
    )
