from __future__ import annotations

from statistics import mean
from typing import Any

from app.rag.evaluation import load_eval_cases
from app.rag.retrieval_diagnostics import analyze_retrieval_result
from app.rag.retrieval_strategies import (
    AVAILABLE_STRATEGIES,
    RetrievalStrategyName,
    retrieve_with_strategy,
)


def evaluate_retrieval_strategies(
    top_k: int = 5,
    strategies: tuple[RetrievalStrategyName, ...] = AVAILABLE_STRATEGIES,
) -> dict[str, Any]:
    cases = load_eval_cases()
    strategy_reports = [
        _evaluate_strategy(strategy_name, cases, top_k=top_k)
        for strategy_name in strategies
    ]
    recommended_default = _recommended_default(strategy_reports)

    return {
        "total_cases": len(cases),
        "strategies": strategy_reports,
        "recommended_default_strategy": recommended_default,
        "passed": all(report["passed"] for report in strategy_reports),
        "warnings": _report_warnings(strategy_reports, recommended_default),
    }


def _evaluate_strategy(
    strategy_name: RetrievalStrategyName,
    cases: list[dict[str, Any]],
    top_k: int,
) -> dict[str, Any]:
    case_reports = [_evaluate_case(strategy_name, case, top_k) for case in cases]
    total_cases = len(case_reports)

    top_k_hits = sum(1 for case in case_reports if case["checks"]["top_k_hit"])
    source_hits = sum(1 for case in case_reports if case["checks"]["expected_source_hit"])
    section_hits = sum(1 for case in case_reports if case["checks"]["expected_section_hit"])
    insufficient_correct = sum(
        1 for case in case_reports if case["checks"]["insufficient_context_correct"]
    )
    governance_presence = sum(
        1 for case in case_reports if case["checks"]["governance_metadata_presence"]
    )
    weak_detection = sum(
        1 for case in case_reports if case["checks"]["weak_retrieval_detection"]
    )

    average_retrieved_chunks = mean(
        [case["retrieved_count"] for case in case_reports]
    ) if case_reports else 0.0

    top_hit_rate = _rate(top_k_hits, total_cases)
    insufficient_rate = _rate(insufficient_correct, total_cases)
    passed = top_hit_rate >= 0.75 and insufficient_rate == 1.0

    return {
        "strategy_name": strategy_name,
        "passed": passed,
        "total_cases": total_cases,
        "top_k_hit_rate": top_hit_rate,
        "expected_source_hit_rate": _rate(source_hits, total_cases),
        "expected_section_hit_rate": _rate(section_hits, total_cases),
        "insufficient_context_correctness": insufficient_rate,
        "governance_metadata_presence": _rate(governance_presence, total_cases),
        "weak_retrieval_detection": _rate(weak_detection, total_cases),
        "average_retrieved_chunks": round(average_retrieved_chunks, 2),
        "cases": case_reports,
    }


def _evaluate_case(
    strategy_name: RetrievalStrategyName,
    case: dict[str, Any],
    top_k: int,
) -> dict[str, Any]:
    contexts = retrieve_with_strategy(
        query=case["query"],
        strategy_name=strategy_name,
        top_k=top_k,
    )
    diagnostics = analyze_retrieval_result(case["query"], contexts)
    expected_drug_name = case.get("expected_drug_name")
    expected_source_files = set(case.get("expected_source_files", []))
    expected_section_titles = set(case.get("expected_section_titles", []))
    expected_insufficient = bool(case["expected_insufficient_context"])

    retrieved_drugs = {context.drug_name.lower() for context in contexts}
    retrieved_source_files = {context.source_file for context in contexts}
    retrieved_section_titles = {context.section_title for context in contexts}

    if expected_drug_name is None:
        top_k_hit = contexts == []
    else:
        top_k_hit = expected_drug_name.lower() in retrieved_drugs

    governance_metadata_presence = True
    if contexts:
        governance_metadata_presence = all(
            context.source_status
            and context.review_status
            and context.clinical_validation_status
            and context.requires_pharmacist_review is not None
            for context in contexts
        )

    weak_retrieval_detection = (
        diagnostics.retrieval_status in {"weak", "insufficient"}
        if expected_insufficient
        else diagnostics.retrieval_status in {"strong", "moderate", "weak"}
    )

    checks = {
        "top_k_hit": top_k_hit,
        "expected_source_hit": expected_source_files.issubset(retrieved_source_files),
        "expected_section_hit": expected_section_titles.issubset(retrieved_section_titles),
        "insufficient_context_correct": diagnostics.insufficient_context is expected_insufficient,
        "governance_metadata_presence": governance_metadata_presence,
        "weak_retrieval_detection": weak_retrieval_detection,
    }

    return {
        "case_id": case["case_id"],
        "query": case["query"],
        "retrieved_count": len(contexts),
        "retrieval_status": diagnostics.retrieval_status,
        "warnings": diagnostics.warnings,
        "checks": checks,
    }


def _recommended_default(strategy_reports: list[dict[str, Any]]) -> str:
    for report in strategy_reports:
        if report["strategy_name"] == "existing_default" and report["passed"]:
            return "existing_default"
    passing = [report for report in strategy_reports if report["passed"]]
    if not passing:
        return "existing_default"
    return sorted(
        passing,
        key=lambda report: (
            report["top_k_hit_rate"],
            report["expected_source_hit_rate"],
            report["expected_section_hit_rate"],
        ),
        reverse=True,
    )[0]["strategy_name"]


def _report_warnings(
    strategy_reports: list[dict[str, Any]],
    recommended_default: str,
) -> list[str]:
    warnings = [
        "Retrieval comparison is an engineering benchmark, not clinical validation."
    ]
    if recommended_default != "existing_default":
        warnings.append(
            "A non-default strategy scored higher, but production retrieval was not changed."
        )
    for report in strategy_reports:
        if report["strategy_name"] != "existing_default" and not report["passed"]:
            warnings.append(
                f"{report['strategy_name']} is diagnostic-only and should not replace the default retriever."
            )
    return warnings


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(count / total, 4)
