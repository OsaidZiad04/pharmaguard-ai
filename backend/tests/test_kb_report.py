import subprocess
import sys
from pathlib import Path


def test_kb_report_script_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/kb_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Total profiles: 15" in result.stdout
    assert "Total enabled profiles: 15" in result.stdout
    assert "Validation status: PASS" in result.stdout
    assert "not clinical validation" in result.stdout
