from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.project_evidence_report import build_project_evidence_report_lines


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_project_evidence_report_contains_core_sections() -> None:
    report = "\n".join(build_project_evidence_report_lines())

    assert "PharmaGuard AI Project Evidence Report" in report
    assert "Phase 4-Final" in report
    assert "RAG evaluation" in report
    assert "Retrieval strategy evaluation" in report
    assert "KB governance" in report
    assert "OCR evaluation" in report
    assert "Safety rules report" in report
    assert "E2E workflow evaluation" in report
    assert "Tesseract benchmark" in report


def test_project_evidence_report_preserves_safety_framing() -> None:
    report = "\n".join(build_project_evidence_report_lines()).lower()

    assert "not clinical validation" in report
    assert "patient-facing output remains disabled" in report
    assert "pharmacist review remains mandatory" in report
    assert "no real patient data" in report


def test_project_evidence_report_script_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/project_evidence_report.py"],
        cwd=BACKEND_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "PharmaGuard AI Project Evidence Report" in result.stdout
    assert "not clinical validation" in result.stdout
