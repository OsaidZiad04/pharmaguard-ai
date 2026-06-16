from app.rag.retrieval_diagnostics import (
    analyze_retrieval_result,
    detect_governance_risk_in_retrieval,
    detect_weak_retrieval,
    summarize_retrieval_quality,
)
from app.rag.retriever import RetrievedContext, retrieve_contexts


def test_retrieval_diagnostics_identifies_insufficient_context() -> None:
    report = analyze_retrieval_result("xyzmed 20 mg counseling", [])

    assert report.retrieval_status == "insufficient"
    assert report.insufficient_context is True
    assert report.pharmacist_review_required is True
    assert any("No local knowledge-base context" in warning for warning in report.warnings)


def test_retrieval_diagnostics_identifies_placeholder_and_review_required_context() -> None:
    contexts = retrieve_contexts("paracetamol counseling", top_k=5)
    report = analyze_retrieval_result("paracetamol counseling", contexts)

    assert report.retrieval_status in {"moderate", "strong"}
    assert report.source_count == 1
    assert report.unique_drug_count == 1
    assert report.governance_warning_count >= 3
    assert report.pharmacist_review_required is True
    assert any("placeholder educational" in warning for warning in report.warnings)
    assert any("not clinically validated" in warning for warning in report.warnings)


def test_retrieval_diagnostics_identifies_weak_context() -> None:
    weak_context = [
        RetrievedContext(
            chunk_id="test:overview:0-0",
            drug_name="testdrug",
            source_file="testdrug.md",
            section_title="Overview",
            text="Short context.",
            score=0.05,
            source_status="placeholder_educational",
            review_status="draft",
            clinical_validation_status="not_validated",
            requires_pharmacist_review=True,
            patient_facing_allowed=False,
        )
    ]

    assert detect_weak_retrieval("testdrug counseling", weak_context) is True


def test_retrieval_diagnostics_summary_shape() -> None:
    contexts = retrieve_contexts("ibuprofen safety notes", top_k=5)
    summary = summarize_retrieval_quality("ibuprofen safety notes", contexts)

    assert summary["retrieval_status"] in {"moderate", "strong"}
    assert summary["source_count"] == 1
    assert summary["pharmacist_review_required"] is True


def test_governance_risk_detector_flags_missing_metadata() -> None:
    warnings = detect_governance_risk_in_retrieval(
        [
            {
                "chunk_id": "x",
                "drug_name": "test",
                "source_file": "test.md",
                "section_title": "Overview",
                "score": 0.5,
            }
        ]
    )

    assert "Retrieved context is missing source governance metadata." in warnings
