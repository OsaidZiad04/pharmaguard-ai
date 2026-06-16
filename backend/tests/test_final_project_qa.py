from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.final_project_qa import build_qa_commands


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_final_project_qa_command_list_contains_required_checks() -> None:
    commands = build_qa_commands()
    labels = {command.label for command in commands}
    joined = "\n".join(" ".join(command.command) for command in commands)

    assert "backend tests" in labels
    assert "RAG evaluation" in labels
    assert "retrieval strategy evaluation" in labels
    assert "KB governance report" in labels
    assert "safety rules report" in labels
    assert "OCR evaluation" in labels
    assert "E2E workflow evaluation" in labels
    assert "Tesseract benchmark" in labels
    assert "project evidence report" in labels
    assert "final demo report" in labels
    assert "frontend typecheck" in labels
    assert "frontend build" in labels
    assert "git diff check" in labels
    assert "project_evidence_report.py" in joined
    assert "final_demo_report.py" in joined


def test_final_project_qa_list_mode_runs_without_executing_suite() -> None:
    result = subprocess.run(
        [sys.executable, "backend/scripts/final_project_qa.py", "--list"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "backend tests" in result.stdout
    assert "project evidence report" in result.stdout
    assert "final demo report" in result.stdout
    assert "git diff check" in result.stdout
