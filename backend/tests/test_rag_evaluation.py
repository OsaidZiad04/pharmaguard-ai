from app.rag.evaluation import load_eval_cases, run_rag_evaluation


def test_rag_evaluation_dataset_has_required_scenarios() -> None:
    cases = load_eval_cases()
    case_ids = {case["case_id"] for case in cases}

    assert "RAG-SUP-001" in case_ids
    assert "RAG-ALIAS-001" in case_ids
    assert "RAG-UNK-001" in case_ids
    assert "RAG-WEAK-001" in case_ids
    assert "RAG-UNSUPPORTED-001" in case_ids
    assert "RAG-MIXED-001" in case_ids


def test_rag_evaluation_runner_passes_current_baseline() -> None:
    report = run_rag_evaluation()

    assert report["total_cases"] >= 8
    assert report["failed_cases"] == 0
    assert report["passed_cases"] == report["total_cases"]
    assert report["retrieval_summary"]["top_k_hit_passed"] == report["total_cases"]
    assert (
        report["generation_safety_summary"]["citations_valid_passed"]
        == report["total_cases"]
    )
