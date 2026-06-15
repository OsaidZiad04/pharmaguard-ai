import subprocess
import sys
from pathlib import Path

from app.services.ocr_service import list_available_ocr_providers


def test_provider_report_lists_safe_local_providers() -> None:
    providers = list_available_ocr_providers()
    provider_names = {provider.provider_name for provider in providers}

    assert provider_names == {"mock_ocr_phase_2a", "synthetic_fixture_phase_2c"}
    assert all(not provider.is_external_provider for provider in providers)
    assert all(not provider.stores_images for provider in providers)
    assert all(not provider.requires_network for provider in providers)


def test_ocr_provider_report_script_runs_successfully() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/ocr_provider_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "mock_ocr_phase_2a" in result.stdout
    assert "synthetic_fixture_phase_2c" in result.stdout
    assert "quality_gate_eligible: True" in result.stdout
    assert "can_be_used_without_network: True" in result.stdout
    assert "allowed_in_current_prototype_mode: True" in result.stdout


def test_existing_provider_report_remains_independent_from_candidate_registry() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/ocr_provider_report.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "tesseract_local_candidate" not in result.stdout
    assert "cloud_ocr_candidate_placeholder" not in result.stdout
