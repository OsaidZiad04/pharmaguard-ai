from collections import Counter
from pathlib import Path
import json
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.workflows.e2e_evaluation import run_e2e_workflow_evaluation  # noqa: E402


E2E_TRACE_EXPORT_PATH = (
    REPO_ROOT / "data" / "evaluation" / "generated" / "e2e_traces.json"
)


def load_or_generate_traces(path: Path = E2E_TRACE_EXPORT_PATH) -> list[dict]:
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    report = run_e2e_workflow_evaluation()
    return [case_result["trace"] for case_result in report["case_results"]]


def build_trace_report_lines(path: Path = E2E_TRACE_EXPORT_PATH) -> list[str]:
    traces = load_or_generate_traces(path)
    step_status_counts = Counter(
        f"{step['step_name']}:{step['status']}"
        for trace in traces
        for step in trace["steps"]
    )
    safety_flag_counts = Counter(
        flag["code"] for trace in traces for flag in trace["safety_flags"]
    )
    pharmacist_review_required = sum(
        1 for trace in traces if trace["pharmacist_review_required"]
    )
    traces_with_sources = sum(
        1
        for trace in traces
        if any(
            step["step_name"] == "rag_retrieval" and step["source_refs"]
            for step in trace["steps"]
        )
    )
    blocked_unsafe_flow = sum(
        1
        for trace in traces
        if any(
            step["step_name"] == "unverified_ocr_downstream_use"
            and step["status"] == "blocked"
            for step in trace["steps"]
        )
    )

    lines = [
        "PharmaGuard AI E2E Trace Report",
        "Synthetic traceability only; this is not clinical validation.",
        f"total traces: {len(traces)}",
        "step completion summary:",
    ]
    lines.extend(
        f"- {key}: {step_status_counts[key]}" for key in sorted(step_status_counts)
    )
    lines.append("safety flag summary:")
    lines.extend(
        f"- {key}: {safety_flag_counts[key]}" for key in sorted(safety_flag_counts)
    )
    lines.extend(
        [
            "pharmacist review summary:",
            f"- pharmacist_review_required traces: {pharmacist_review_required}",
            "source grounding summary:",
            f"- traces with RAG source refs: {traces_with_sources}",
            "blocked unsafe-flow summary:",
            f"- unverified OCR downstream use blocked: {blocked_unsafe_flow}",
        ]
    )
    return lines


def main() -> int:
    for line in build_trace_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
