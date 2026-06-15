from app.ocr import provider_dependencies
from app.ocr.provider_dependencies import (
    get_provider_dependency_status,
    check_python_package_available,
)


def test_python_package_available_check_is_local_and_deterministic() -> None:
    assert check_python_package_available("json") is True
    assert check_python_package_available("pharmaguard_missing_package_xyz") is False


def test_tesseract_dependency_status_can_report_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        provider_dependencies,
        "check_python_package_available",
        lambda package_name: False,
    )
    monkeypatch.setattr(
        provider_dependencies,
        "check_tesseract_available",
        lambda: False,
    )

    status = get_provider_dependency_status("tesseract_local_candidate")

    assert status.available is False
    assert status.python_package_available is False
    assert status.system_binary_available is False
    assert "not detected" in status.details


def test_mock_and_synthetic_providers_have_no_optional_dependencies() -> None:
    for provider_id in ["mock_ocr_phase_2a", "synthetic_fixture_phase_2c"]:
        status = get_provider_dependency_status(provider_id)

        assert status.available is True
        assert status.checked_dependencies == []


def test_unknown_provider_dependency_status_is_safe() -> None:
    status = get_provider_dependency_status("unknown_provider")

    assert status.available is False
    assert "No dependency check" in status.details
