import json
import subprocess
import sys
from pathlib import Path

from scripts.e2e_trace_report import build_trace_report_lines
from scripts.export_e2e_traces import export_e2e_traces


BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_EXPORT_PATH = BACKEND_ROOT / ".test-output" / "e2e_traces.json"


def test_trace_export_writes_synthetic_trace_file() -> None:
    try:
        summary = export_e2e_traces(TEST_EXPORT_PATH)

        assert TEST_EXPORT_PATH.exists()
        assert summary["total_traces"] == 10
        assert summary["pharmacist_review_required_count"] == 10
        traces = json.loads(TEST_EXPORT_PATH.read_text(encoding="utf-8"))
        assert len(traces) == 10
        assert all(trace["trace_id"] for trace in traces)
        assert all(trace["contains_real_patient_data"] is False for trace in traces)
        assert all(trace["stores_raw_image_bytes"] is False for trace in traces)
    finally:
        _cleanup_test_export()


def test_trace_report_builds_summary_from_exported_file() -> None:
    try:
        export_e2e_traces(TEST_EXPORT_PATH)

        report_lines = build_trace_report_lines(TEST_EXPORT_PATH)
        report_text = "\n".join(report_lines)

        assert "total traces: 10" in report_text
        assert "unverified OCR downstream use blocked: 10" in report_text
        assert "pharmacist_review_required traces: 10" in report_text
        assert "traces with RAG source refs: 8" in report_text
    finally:
        _cleanup_test_export()


def test_trace_export_script_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/export_e2e_traces.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "total traces: 10" in result.stdout
    assert "pharmacist_review_required count: 10" in result.stdout


def test_trace_report_script_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/e2e_trace_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PharmaGuard AI E2E Trace Report" in result.stdout
    assert "blocked unsafe-flow summary" in result.stdout


def _cleanup_test_export() -> None:
    if TEST_EXPORT_PATH.exists():
        TEST_EXPORT_PATH.unlink()
    if TEST_EXPORT_PATH.parent.exists() and not any(TEST_EXPORT_PATH.parent.iterdir()):
        TEST_EXPORT_PATH.parent.rmdir()
