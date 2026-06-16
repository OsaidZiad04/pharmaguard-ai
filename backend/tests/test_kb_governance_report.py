import subprocess
import sys
from pathlib import Path


def test_kb_governance_report_script_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/kb_governance_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Total profiles: 15" in result.stdout
    assert "Enabled for RAG: 15" in result.stdout
    assert "Governance status: PASS" in result.stdout
    assert "Blocking issues: 0" in result.stdout
    assert "not clinical validation" in result.stdout
