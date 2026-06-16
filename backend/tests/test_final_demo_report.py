from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.final_demo_report import (
    build_final_demo_report_lines,
    load_final_demo_cases,
)


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_final_demo_cases_load_and_remain_synthetic() -> None:
    cases = load_final_demo_cases()

    assert 5 <= len(cases) <= 7
    for case in cases:
        assert case["case_id"].startswith("DEMO-")
        assert case["title"]
        assert case["scenario_type"]
        assert isinstance(case["expected_medications"], list)
        assert case["expected_safety_findings"]
        assert case["expected_retrieval_behavior"]
        assert case["expected_pharmacist_action"]
        assert case["demo_talking_points"]

    serialized = "\n".join(str(case) for case in cases).lower()
    assert "synthetic" in serialized
    assert "john doe" not in serialized
    assert "jane doe" not in serialized


def test_final_demo_report_contains_safety_and_story_sections() -> None:
    report = "\n".join(build_final_demo_report_lines())

    assert "PharmaGuard AI Final Demo Report" in report
    assert "synthetic scenarios are not clinical validation" in report
    assert "pharmacist-centered" in report
    assert "Patient-facing output remains disabled" in report
    assert "Unsupported medication" in report


def test_final_demo_report_script_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/final_demo_report.py"],
        cwd=BACKEND_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "PharmaGuard AI Final Demo Report" in result.stdout
    assert "not clinical validation" in result.stdout
