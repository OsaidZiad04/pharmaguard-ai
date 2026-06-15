from __future__ import annotations

from app.ocr.local_tesseract_provider import (
    ProviderUnavailableError,
    TesseractLocalOcrProvider,
)
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


def get_ocr_provider(provider_name: str = "mock") -> BaseOcrProvider:
    """Select a safe local OCR provider.

    Unknown local provider names fall back to the deterministic mock provider.
    Explicit external/cloud provider names are rejected because Phase 2C does
    not permit networked OCR integrations.
    """
    normalized_name = (provider_name or "mock").strip().lower()
    if normalized_name in BLOCKED_EXTERNAL_PROVIDER_NAMES:
        raise ValueError("External OCR providers are not enabled in prototype mode.")

    provider_class = PROVIDER_ALIASES.get(normalized_name, MockOcrProvider)
    provider = provider_class()
    if normalized_name in INACTIVE_PROVIDER_NAMES or not provider.enabled_by_default:
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
    """Return active providers plus inactive adapter skeletons for reporting."""
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
    provider_name: str = "mock",
) -> OcrExtractedText:
    """Run a safe local OCR provider without external API calls."""
    ocr_provider = provider or get_ocr_provider(provider_name)
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
