from __future__ import annotations

from app.ocr.activation_policy import (
    evaluate_ocr_provider_activation,
    normalize_ocr_mode,
)
from app.ocr.local_tesseract_provider import (
    ProviderUnavailableError,
    TesseractLocalOcrProvider,
)
from app.ocr.ocr_config import OcrRuntimeConfig, get_ocr_runtime_config
from app.ocr.provider_dependencies import ProviderDependencyStatus
from app.ocr.providers import (
    BaseOcrProvider,
    MockOcrProvider,
    SyntheticFixtureOcrProvider,
    build_privacy_warnings,
    detect_possible_identifiers,
)
from app.schemas.ocr import OcrExtractedText, PrivacyWarning


PROVIDER_ALIASES = {
    "mock": MockOcrProvider,
    MockOcrProvider.provider_name: MockOcrProvider,
    "synthetic_fixture": SyntheticFixtureOcrProvider,
    SyntheticFixtureOcrProvider.provider_name: SyntheticFixtureOcrProvider,
    "tesseract": TesseractLocalOcrProvider,
    TesseractLocalOcrProvider.provider_name: TesseractLocalOcrProvider,
}
BLOCKED_EXTERNAL_PROVIDER_NAMES = {
    "external",
    "external_api",
    "cloud",
    "google_vision",
    "azure_ocr",
    "aws_textract",
}
INACTIVE_PROVIDER_NAMES = {
    "tesseract",
    TesseractLocalOcrProvider.provider_name,
}


def get_ocr_provider(
    provider_name: str | None = None,
    allow_benchmark_provider: bool = False,
    ocr_mode: str | None = None,
    config: OcrRuntimeConfig | None = None,
    dependency_status: ProviderDependencyStatus | None = None,
    benchmark_gate_passed: bool | None = None,
) -> BaseOcrProvider:
    """Select a safe local OCR provider.

    Unknown local provider names fall back to the deterministic mock provider.
    Explicit external/cloud provider names are rejected because Phase 2C does
    not permit networked OCR integrations.
    """
    config = config or get_ocr_runtime_config()
    requested_name = provider_name or config.default_provider
    normalized_name = (requested_name or "mock").strip().lower()
    if normalized_name in BLOCKED_EXTERNAL_PROVIDER_NAMES:
        raise ValueError("External OCR providers are not enabled in prototype mode.")

    provider_class = PROVIDER_ALIASES.get(normalized_name, MockOcrProvider)
    mode = normalize_ocr_mode(
        ocr_mode
        or ("benchmark" if allow_benchmark_provider else config.ocr_mode)
    )
    policy_provider_id = provider_class.provider_name
    activation = evaluate_ocr_provider_activation(
        provider_id=policy_provider_id,
        mode=mode,
        config=config,
        dependency_status=dependency_status,
        benchmark_gate_passed=benchmark_gate_passed,
    )
    if not activation.allowed:
        raise ValueError(
            "OCR activation policy blocked provider "
            f"{policy_provider_id} for mode {mode}: "
            + "; ".join(activation.blocking_reasons)
        )

    if provider_class is TesseractLocalOcrProvider and allow_benchmark_provider:
        provider = TesseractLocalOcrProvider(benchmark_mode=True)
    elif provider_class is TesseractLocalOcrProvider and mode == "prototype_explicit":
        provider = TesseractLocalOcrProvider(explicitly_enabled=True)
    else:
        provider = provider_class()
    if normalized_name in INACTIVE_PROVIDER_NAMES or not provider.enabled_by_default:
        if (
            allow_benchmark_provider
            and isinstance(provider, TesseractLocalOcrProvider)
            and not provider.is_external_provider
            and not provider.requires_network
            and not provider.stores_images
        ):
            return provider
        dependency_status = (
            provider.dependency_status()
            if isinstance(provider, TesseractLocalOcrProvider)
            else None
        )
        dependency_detail = (
            f" Dependency status: {dependency_status.details}"
            if dependency_status is not None
            else ""
        )
        raise ValueError(
            "Requested OCR provider is adapter-defined but inactive in prototype mode."
            f"{dependency_detail}"
        )
    if provider.is_external_provider or provider.requires_network or provider.stores_images:
        raise ValueError("Unsafe OCR provider metadata for prototype mode.")
    return provider


def list_available_ocr_providers() -> list[BaseOcrProvider]:
    return [MockOcrProvider(), SyntheticFixtureOcrProvider()]


def list_known_ocr_provider_adapters() -> list[BaseOcrProvider]:
    """Return active providers plus inactive adapters for reporting."""
    return [
        MockOcrProvider(),
        SyntheticFixtureOcrProvider(),
        TesseractLocalOcrProvider(),
    ]


def extract_text_from_image(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    provider: BaseOcrProvider | None = None,
    provider_name: str | None = None,
    allow_benchmark_provider: bool = False,
    ocr_mode: str | None = None,
    config: OcrRuntimeConfig | None = None,
    dependency_status: ProviderDependencyStatus | None = None,
    benchmark_gate_passed: bool | None = None,
) -> OcrExtractedText:
    """Run a safe local OCR provider without external API calls."""
    config = config or get_ocr_runtime_config()
    ocr_provider = provider or get_ocr_provider(
        provider_name=provider_name,
        allow_benchmark_provider=allow_benchmark_provider,
        ocr_mode=ocr_mode,
        config=config,
        dependency_status=dependency_status,
        benchmark_gate_passed=benchmark_gate_passed,
    )
    mode = normalize_ocr_mode(
        ocr_mode
        or ("benchmark" if allow_benchmark_provider else config.ocr_mode)
    )
    activation = evaluate_ocr_provider_activation(
        provider_id=ocr_provider.provider_name,
        mode=mode,
        config=config,
        dependency_status=dependency_status,
        benchmark_gate_passed=benchmark_gate_passed,
    )
    if not activation.allowed:
        raise ValueError(
            "OCR activation policy blocked provider "
            f"{ocr_provider.provider_name} for mode {mode}: "
            + "; ".join(activation.blocking_reasons)
        )
    if not ocr_provider.supports_content_type(content_type):
        raise ValueError(f"Provider does not support content type: {content_type}")
    try:
        return ocr_provider.extract_text(file_bytes, filename, content_type)
    except ProviderUnavailableError as error:
        raise ValueError(str(error)) from error


def confirm_corrected_ocr_text(corrected_text: str) -> tuple[list[str], list[PrivacyWarning]]:
    """Validate pharmacist-corrected text for privacy warnings before analysis."""
    detected_identifiers = detect_possible_identifiers(corrected_text)
    return detected_identifiers, build_privacy_warnings(detected_identifiers)
