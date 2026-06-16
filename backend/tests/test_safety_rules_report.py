import subprocess
import sys
from pathlib import Path

from scripts.safety_rules_report import run_safety_rules_report


def test_safety_rules_report_passes_synthetic_scenarios() -> None:
    report = run_safety_rules_report()

    assert report["total_scenarios"] == 10
    assert report["failed_scenarios"] == 0
    assert report["passed_scenarios"] == 10
    assert report["pharmacist_review_required_count"] == 10
    assert report["patient_facing_blocked_count"] == 10
    assert "unsupported_medication_detected" in report["rules_triggered"]
    assert "not_clinically_validated" in report["rules_triggered"]


def test_safety_rules_report_script_runs() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/safety_rules_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "passed scenarios: 10" in result.stdout
    assert "not clinical validation" in result.stdout
