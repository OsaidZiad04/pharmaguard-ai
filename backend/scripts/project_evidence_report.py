from __future__ import annotations

from pathlib import Path
import sys
from typing import Callable


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.kb.governance import validate_governance_metadata  # noqa: E402
from app.kb.validator import build_coverage_report  # noqa: E402
from app.ocr.evaluation import run_ocr_evaluation  # noqa: E402
from app.ocr.provider_candidates import list_provider_candidates  # noqa: E402
from app.ocr.provider_dependencies import get_provider_dependency_status  # noqa: E402
from app.ocr.tesseract_benchmark import run_tesseract_benchmark  # noqa: E402
from app.rag.evaluation import run_rag_evaluation  # noqa: E402
from app.rag.retrieval_evaluation import evaluate_retrieval_strategies  # noqa: E402
from app.workflows.e2e_evaluation import run_e2e_workflow_evaluation  # noqa: E402
from scripts.safety_rules_report import run_safety_rules_report  # noqa: E402


def build_project_evidence_report_lines() -> list[str]:
    rag = _safe("RAG evaluation", run_rag_evaluation)
    retrieval = _safe("retrieval strategy evaluation", evaluate_retrieval_strategies)
    kb = _safe("KB report", build_coverage_report)
    governance = _safe("KB governance report", validate_governance_metadata)
    ocr = _safe("OCR evaluation", run_ocr_evaluation)
    safety = _safe("safety rules report", run_safety_rules_report)
    e2e = _safe("E2E workflow evaluation", run_e2e_workflow_evaluation)
    tesseract = _safe("Tesseract benchmark", run_tesseract_benchmark)
    candidates = _safe("OCR candidates", list_provider_candidates)

    lines = [
        "PharmaGuard AI Project Evidence Report",
        "current phase: Phase 5 - One-Click Demo & Local Launch Experience",
        "safety positioning: pharmacist-centered prototype; not clinical validation; not patient-facing final advice.",
        "backend test status: run `python -m pytest` from backend/ for the current authoritative count.",
        "frontend build status: run `npm.cmd run typecheck` and `npm.cmd run build` from frontend/.",
        "",
        "Evaluation summary:",
        _rag_line(rag),
        _retrieval_line(retrieval),
        _kb_line(kb),
        _governance_line(governance),
        _ocr_line(ocr),
        _candidate_line(candidates),
        _activation_policy_line(),
        _safety_line(safety),
        _e2e_line(e2e),
        _traceability_line(),
        _tesseract_line(tesseract),
        "",
        "Known limitations:",
        "- Draft placeholder educational KB only; no clinical validation.",
        "- Patient-facing output remains disabled.",
        "- Pharmacist review remains mandatory.",
        "- No real OCR provider is default; Tesseract remains optional and policy-gated.",
        "- No real interaction, contraindication, diagnosis, or treatment decision engine.",
        "- No real patient data, external medical APIs, or trusted-source ingestion.",
        "",
        "Demo readiness checklist:",
        "- Use the one-click Windows launch scripts or the manual launch fallback.",
        "- Run the demo health check before reviewer sessions.",
        "- Run final QA commands before recording or presenting.",
        "- Use only synthetic demo cases and fixtures.",
        "- Show OCR correction boundary before analysis.",
        "- Show source grounding and governance warnings.",
        "- Show safety-rule findings as pharmacist prompts, not final advice.",
        "- State limitations clearly in the demo.",
    ]
    return lines


def main() -> int:
    for line in build_project_evidence_report_lines():
        print(line)
    return 0


def _safe(label: str, fn: Callable):
    try:
        return {"ok": True, "value": fn()}
    except Exception as error:  # pragma: no cover - defensive report path
        return {"ok": False, "label": label, "error": str(error)}


def _rag_line(result: dict) -> str:
    if not result["ok"]:
        return f"- RAG evaluation: unavailable ({result['error']})"
    report = result["value"]
    return f"- RAG evaluation: {report['passed_cases']}/{report['total_cases']} passed."


def _retrieval_line(result: dict) -> str:
    if not result["ok"]:
        return f"- Retrieval strategy evaluation: unavailable ({result['error']})"
    report = result["value"]
    status = "PASS" if report["passed"] else "REVIEW"
    return (
        f"- Retrieval strategy evaluation: {status}; recommended default "
        f"{report['recommended_default_strategy']}."
    )


def _kb_line(result: dict) -> str:
    if not result["ok"]:
        return f"- KB report: unavailable ({result['error']})"
    report = result["value"]
    blocking = [
        issue for issue in report.validation_report.issues if issue.severity == "error"
    ]
    return (
        f"- KB report: {'PASS' if report.validation_report.valid else 'FAIL'}; "
        f"{report.total_profiles} profiles; {len(blocking)} blockers."
    )


def _governance_line(result: dict) -> str:
    if not result["ok"]:
        return f"- KB governance: unavailable ({result['error']})"
    report = result["value"]
    return (
        f"- KB governance: {'PASS' if report.valid else 'FAIL'}; "
        f"{len(report.blocking_issues)} blockers; "
        f"{report.patient_facing_allowed_count} patient-facing profiles."
    )


def _ocr_line(result: dict) -> str:
    if not result["ok"]:
        return f"- OCR evaluation: unavailable ({result['error']})"
    report = result["value"]
    return (
        f"- OCR evaluation: {report['passed_cases']}/{report['total_cases']} passed; "
        f"{report['fixture_backed_cases']} fixture-backed cases."
    )


def _candidate_line(result: dict) -> str:
    if not result["ok"]:
        return f"- OCR provider/candidate summary: unavailable ({result['error']})"
    candidates = result["value"]
    implemented = sum(1 for candidate in candidates if candidate.current_status == "implemented")
    disallowed = sum(
        1 for candidate in candidates if candidate.current_status == "disallowed_for_prototype"
    )
    return (
        f"- OCR provider/candidate summary: {len(candidates)} candidates; "
        f"{implemented} implemented; {disallowed} disallowed for prototype."
    )


def _activation_policy_line() -> str:
    tesseract_status = get_provider_dependency_status("tesseract_local_candidate")
    return (
        "- OCR activation policy: mock default; external OCR blocked; "
        f"Tesseract dependency_available={tesseract_status.available}."
    )


def _safety_line(result: dict) -> str:
    if not result["ok"]:
        return f"- Safety rules report: unavailable ({result['error']})"
    report = result["value"]
    return (
        f"- Safety rules report: {report['passed_scenarios']}/"
        f"{report['total_scenarios']} scenarios passed; "
        f"patient-facing blocked count {report['patient_facing_blocked_count']}."
    )


def _e2e_line(result: dict) -> str:
    if not result["ok"]:
        return f"- E2E workflow evaluation: unavailable ({result['error']})"
    report = result["value"]
    return f"- E2E workflow evaluation: {report['passed_cases']}/{report['total_cases']} passed."


def _traceability_line() -> str:
    trace_path = REPO_ROOT / "data" / "evaluation" / "generated" / "e2e_traces.json"
    status = "available" if trace_path.exists() else "regenerate with export_e2e_traces.py"
    return f"- Traceability summary: synthetic trace file {status}."


def _tesseract_line(result: dict) -> str:
    if not result["ok"]:
        return f"- Tesseract benchmark: unavailable ({result['error']})"
    report = result["value"]
    return (
        f"- Tesseract benchmark: {report['status']}; "
        f"dependency_available={report['dependency_available']}; "
        f"quality_gate_status={report['quality_gate_status']}."
    )


if __name__ == "__main__":
    raise SystemExit(main())
