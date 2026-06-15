from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.workflows.e2e_evaluation import run_e2e_workflow_evaluation  # noqa: E402


def build_e2e_workflow_report_lines(report: dict | None = None) -> list[str]:
    report = report or run_e2e_workflow_evaluation()
    lines = [
        "PharmaGuard AI End-to-End OCR-to-RAG Workflow Evaluation",
        "warning: synthetic workflow evaluation only; this is not clinical validation.",
        f"total cases: {report['total_cases']}",
        f"passed cases: {report['passed_cases']}",
        f"failed cases: {report['failed_cases']}",
        "privacy warning summary:",
        f"- passed: {report['privacy_warning_summary']['passed']}",
        f"- failed: {report['privacy_warning_summary']['failed']}",
        "medication extraction summary:",
        f"- passed: {report['medication_extraction_summary']['passed']}",
        f"- failed: {report['medication_extraction_summary']['failed']}",
        "RAG source grounding summary:",
        f"- passed: {report['rag_source_grounding_summary']['passed']}",
        f"- failed: {report['rag_source_grounding_summary']['failed']}",
        "counseling generation summary:",
        f"- passed: {report['counseling_generation_summary']['passed']}",
        f"- failed: {report['counseling_generation_summary']['failed']}",
        "safety summary:",
        f"- passed: {report['safety_summary']['passed']}",
        f"- failed: {report['safety_summary']['failed']}",
        "pharmacist review required summary:",
        f"- passed: {report['pharmacist_review_required_summary']['passed']}",
        f"- failed: {report['pharmacist_review_required_summary']['failed']}",
        "per-case status:",
    ]

    for case in report["case_results"]:
        status = "PASS" if case["passed"] else "FAIL"
        lines.append(
            f"- {status} {case['case_id']} | extracted={case['extracted_medications']} "
            f"| sources={case['retrieved_sources']} | insufficient={case['insufficient_context']} "
            f"| failures={case['failed_checks']}"
        )

    return lines


def main() -> int:
    report = run_e2e_workflow_evaluation()
    for line in build_e2e_workflow_report_lines(report):
        print(line)
    return 0 if report["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
