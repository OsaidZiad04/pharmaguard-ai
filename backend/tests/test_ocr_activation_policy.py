from app.ocr.activation_policy import (
    evaluate_ocr_provider_activation,
    is_provider_allowed_for_mode,
    require_correction_gate,
)
from app.ocr.ocr_config import OcrRuntimeConfig, get_ocr_runtime_config
from app.ocr.provider_dependencies import (
    MOCK_PROVIDER_ID,
    TESSERACT_PROVIDER_ID,
    ProviderDependencyStatus,
)


def test_safe_defaults_apply_without_environment(monkeypatch) -> None:
    for name in [
        "PHARMAGUARD_OCR_DEFAULT_PROVIDER",
        "PHARMAGUARD_OCR_MODE",
        "PHARMAGUARD_ENABLE_TESSERACT_PROTOTYPE",
        "PHARMAGUARD_ALLOW_EXTERNAL_OCR",
        "PHARMAGUARD_TESSERACT_BENCHMARK_PASSED",
    ]:
        monkeypatch.delenv(name, raising=False)

    config = get_ocr_runtime_config()

    assert config.default_provider == MOCK_PROVIDER_ID
    assert config.ocr_mode == "default_workflow"
    assert config.enable_tesseract_prototype is False
    assert config.allow_external_ocr is False
    assert config.tesseract_benchmark_passed is False


def test_mock_provider_is_default_workflow_provider() -> None:
    result = evaluate_ocr_provider_activation(MOCK_PROVIDER_ID, "default_workflow")

    assert result.allowed is True
    assert result.default_provider is True
    assert result.correction_gate_required is True
    assert result.production_allowed is False


def test_tesseract_is_blocked_in_default_workflow() -> None:
    result = evaluate_ocr_provider_activation(
        TESSERACT_PROVIDER_ID,
        "default_workflow",
        dependency_status=_available_tesseract_dependency_status(),
        benchmark_gate_passed=True,
    )

    assert result.allowed is False
    assert "Tesseract is blocked in default_workflow mode." in result.blocking_reasons


def test_tesseract_is_allowed_for_benchmark_when_dependencies_are_available() -> None:
    result = evaluate_ocr_provider_activation(
        TESSERACT_PROVIDER_ID,
        "benchmark",
        dependency_status=_available_tesseract_dependency_status(),
    )

    assert result.allowed is True
    assert result.correction_gate_required is True


def test_tesseract_is_blocked_for_prototype_when_flag_is_false() -> None:
    result = evaluate_ocr_provider_activation(
        TESSERACT_PROVIDER_ID,
        "prototype_explicit",
        config=_config(enable_tesseract=False, benchmark_passed=True),
        dependency_status=_available_tesseract_dependency_status(),
    )

    assert result.allowed is False
    assert "PHARMAGUARD_ENABLE_TESSERACT_PROTOTYPE is false." in result.blocking_reasons


def test_tesseract_can_be_policy_allowed_for_explicit_prototype() -> None:
    result = evaluate_ocr_provider_activation(
        TESSERACT_PROVIDER_ID,
        "prototype_explicit",
        config=_config(enable_tesseract=True, benchmark_passed=True),
        dependency_status=_available_tesseract_dependency_status(),
    )

    assert result.allowed is True
    assert result.default_provider is False
    assert result.production_allowed is False
    assert result.correction_gate_required is True


def test_tesseract_prototype_requires_recorded_benchmark_pass() -> None:
    result = evaluate_ocr_provider_activation(
        TESSERACT_PROVIDER_ID,
        "prototype_explicit",
        config=_config(enable_tesseract=True, benchmark_passed=False),
        dependency_status=_available_tesseract_dependency_status(),
    )

    assert result.allowed is False
    assert (
        "Tesseract prototype mode requires a recorded passing synthetic benchmark."
        in result.blocking_reasons
    )


def test_cloud_ocr_remains_blocked() -> None:
    result = evaluate_ocr_provider_activation(
        "cloud_ocr_candidate_placeholder",
        "prototype_explicit",
    )

    assert result.allowed is False
    assert "External/cloud OCR providers are blocked." in result.blocking_reasons


def test_correction_gate_is_mandatory_for_all_known_providers() -> None:
    for provider_id in [
        "mock_ocr_phase_2a",
        "synthetic_fixture_phase_2c",
        "tesseract_local_candidate",
        "cloud_ocr_candidate_placeholder",
    ]:
        assert require_correction_gate(provider_id) is True


def test_is_provider_allowed_for_mode_uses_safe_defaults() -> None:
    assert is_provider_allowed_for_mode(MOCK_PROVIDER_ID, "default_workflow") is True
    assert is_provider_allowed_for_mode(TESSERACT_PROVIDER_ID, "default_workflow") is False


def _config(enable_tesseract: bool, benchmark_passed: bool) -> OcrRuntimeConfig:
    return OcrRuntimeConfig(
        default_provider=MOCK_PROVIDER_ID,
        ocr_mode="default_workflow",
        enable_tesseract_prototype=enable_tesseract,
        allow_external_ocr=False,
        tesseract_benchmark_passed=benchmark_passed,
        warnings=[],
    )


def _available_tesseract_dependency_status() -> ProviderDependencyStatus:
    return ProviderDependencyStatus(
        provider_id=TESSERACT_PROVIDER_ID,
        available=True,
        python_package_available=True,
        system_binary_available=True,
        checked_dependencies=["pytesseract", "Pillow", "tesseract_binary"],
        details="synthetic available dependency status",
    )
