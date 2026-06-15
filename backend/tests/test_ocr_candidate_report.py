import subprocess
import sys
from pathlib import Path


def test_ocr_candidate_report_script_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/ocr_candidate_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "total candidates: 5" in result.stdout
    assert "implemented candidates: 2" in result.stdout
    assert "planned candidates: 2" in result.stdout
    assert "disallowed candidates: 1" in result.stdout
    assert "cloud_ocr_candidate_placeholder" in result.stdout
    assert "not clinical validation" in result.stdout
