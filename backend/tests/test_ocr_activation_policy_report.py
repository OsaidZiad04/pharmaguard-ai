import subprocess
import sys
from pathlib import Path


def test_ocr_activation_policy_report_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/ocr_activation_policy_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "OCR Activation Policy Report" in result.stdout
    assert "default_provider: mock_ocr_phase_2a" in result.stdout
    assert "tesseract_local_candidate" in result.stdout
    assert "cloud_ocr_candidate_placeholder" in result.stdout
    assert "correction_gate_required" in result.stdout
    assert "not clinical validation" in result.stdout
