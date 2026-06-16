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


def export_e2e_traces(output_path: Path = E2E_TRACE_EXPORT_PATH) -> dict:
    report = run_e2e_workflow_evaluation()
    traces = [case_result["trace"] for case_result in report["case_results"]]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(traces, file, indent=2, sort_keys=True)
        file.write("\n")

    return {
        "output_path": str(output_path),
        "total_traces": len(traces),
        "completed_traces": sum(
            1
            for trace in traces
            if trace["final_status"] in {"completed", "completed_with_warnings"}
        ),
        "blocked_traces": sum(
            1 for trace in traces if trace["final_status"] == "blocked"
        ),
        "pharmacist_review_required_count": sum(
            1 for trace in traces if trace["pharmacist_review_required"]
        ),
        "safety_flags_count": sum(len(trace["safety_flags"]) for trace in traces),
    }


def build_export_report_lines(summary: dict) -> list[str]:
    return [
        "PharmaGuard AI E2E Trace Export",
        "Synthetic trace export only; no raw images or real patient data are stored.",
        f"output_path: {summary['output_path']}",
        f"total traces: {summary['total_traces']}",
        f"completed traces: {summary['completed_traces']}",
        f"blocked traces: {summary['blocked_traces']}",
        (
            "pharmacist_review_required count: "
            f"{summary['pharmacist_review_required_count']}"
        ),
        f"safety flags count: {summary['safety_flags_count']}",
    ]


def main() -> int:
    summary = export_e2e_traces()
    for line in build_export_report_lines(summary):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
