import json
from pathlib import Path
from typing import Any

from app.rag.citation_validator import validate_generated_citations
from app.rag.generator import INSUFFICIENT_CONTEXT_MESSAGE, generate_grounded_answer
from app.rag.retriever import RetrievedContext, retrieve_contexts

DEFAULT_EVAL_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "evaluation" / "rag_eval_cases.json"
)
FINAL_ADVICE_FORBIDDEN_TERMS = (
    "this is final medical advice",
    "no pharmacist review needed",
    "safe for every patient",
    "recommended dose",
)


def load_eval_cases(path: Path | None = None) -> list[dict[str, Any]]:
    eval_path = path or DEFAULT_EVAL_PATH
    with eval_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_rag_evaluation(
    eval_path: Path | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    cases = load_eval_cases(eval_path)
    case_reports = [_evaluate_case(case, top_k=top_k) for case in cases]
    passed_cases = [case for case in case_reports if case["passed"]]
    failed_cases = [case for case in case_reports if not case["passed"]]

    return {
        "total_cases": len(case_reports),
        "passed_cases": len(passed_cases),
        "failed_cases": len(failed_cases),
        "cases": case_reports,
        "retrieval_summary": _summarize(case_reports, "retrieval_checks"),
        "generation_safety_summary": _summarize(case_reports, "generation_checks"),
    }


def _evaluate_case(case: dict[str, Any], top_k: int) -> dict[str, Any]:
    query = case["query"]
    contexts = retrieve_contexts(query=query, top_k=top_k)
    answer = generate_grounded_answer(query, contexts)
    insufficient_context = INSUFFICIENT_CONTEXT_MESSAGE in answer.lower()

    retrieval_checks = _retrieval_checks(case, contexts, insufficient_context)
    generation_checks = _generation_checks(case, contexts, answer)
    all_checks = {**retrieval_checks, **generation_checks}

    return {
        "case_id": case["case_id"],
        "query": query,
        "passed": all(all_checks.values()),
        "retrieved_count": len(contexts),
        "retrieved_sources": [
            {
                "chunk_id": context.chunk_id,
                "drug_name": context.drug_name,
                "source_file": context.source_file,
                "section_title": context.section_title,
                "score": context.score,
            }
            for context in contexts
        ],
        "insufficient_context": insufficient_context,
        "retrieval_checks": retrieval_checks,
        "generation_checks": generation_checks,
        "notes": case.get("notes", ""),
    }


def _retrieval_checks(
    case: dict[str, Any],
    contexts: list[RetrievedContext],
    insufficient_context: bool,
) -> dict[str, bool]:
    expected_drug_name = case.get("expected_drug_name")
    expected_source_files = set(case.get("expected_source_files", []))
    expected_section_titles = set(case.get("expected_section_titles", []))
    retrieved_drugs = {context.drug_name.lower() for context in contexts}
    retrieved_source_files = {context.source_file for context in contexts}
    retrieved_section_titles = {context.section_title for context in contexts}

    return {
        "top_k_hit": (
            not contexts
            if expected_drug_name is None
            else expected_drug_name.lower() in retrieved_drugs
        ),
        "source_file_hit": expected_source_files.issubset(retrieved_source_files),
        "section_hit": expected_section_titles.issubset(retrieved_section_titles),
        "insufficient_context_correct": (
            insufficient_context is bool(case["expected_insufficient_context"])
        ),
    }


def _generation_checks(
    case: dict[str, Any],
    contexts: list[RetrievedContext],
    answer: str,
) -> dict[str, bool]:
    lowered_answer = answer.lower()
    citation_report = validate_generated_citations(answer, contexts)
    must_include_terms = case.get("must_include_terms", [])
    must_not_include_terms = case.get("must_not_include_terms", [])

    required_terms_present = all(
        term.lower() in lowered_answer for term in must_include_terms
    )
    forbidden_terms_absent = all(
        term.lower() not in lowered_answer for term in must_not_include_terms
    )
    final_advice_language_absent = all(
        term not in lowered_answer for term in FINAL_ADVICE_FORBIDDEN_TERMS
    )

    return {
        "required_terms_present": required_terms_present,
        "forbidden_terms_absent": forbidden_terms_absent,
        "draft_or_review_framing_present": (
            "draft" in lowered_answer and "pharmacist review" in lowered_answer
        ),
        "unsupported_unavailable_information_not_invented": forbidden_terms_absent,
        "final_medical_advice_language_absent": final_advice_language_absent,
        "citations_valid": citation_report.valid,
    }


def _summarize(case_reports: list[dict[str, Any]], check_group: str) -> dict[str, int]:
    summary: dict[str, int] = {}
    for case in case_reports:
        for check_name, passed in case[check_group].items():
            key = f"{check_name}_{'passed' if passed else 'failed'}"
            summary[key] = summary.get(key, 0) + 1
    return summary
