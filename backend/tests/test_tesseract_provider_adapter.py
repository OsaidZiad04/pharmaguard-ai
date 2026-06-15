import pytest

from app.ocr.local_tesseract_provider import (
    ProviderUnavailableError,
    TesseractLocalOcrProvider,
)
from app.services.ocr_service import extract_text_from_image, get_ocr_provider


def test_tesseract_provider_imports_without_optional_dependencies() -> None:
    provider = TesseractLocalOcrProvider()

    assert provider.provider_name == "tesseract_local_candidate"
    assert provider.is_external_provider is False
    assert provider.stores_images is False
    assert provider.requires_network is False
    assert provider.requires_system_dependency is True
    assert provider.enabled_by_default is False
    assert provider.prototype_allowed is False


def test_tesseract_provider_dependency_status_is_structured() -> None:
    provider = TesseractLocalOcrProvider()
    status = provider.dependency_status()

    assert status.provider_id == "tesseract_local_candidate"
    assert "pytesseract" in status.checked_dependencies
    assert "tesseract_binary" in status.checked_dependencies


def test_tesseract_provider_extract_raises_controlled_unavailable_error() -> None:
    provider = TesseractLocalOcrProvider()

    with pytest.raises(ProviderUnavailableError, match="disabled by default"):
        provider.extract_text(
            file_bytes=b"synthetic-image",
            filename="synthetic.png",
            content_type="image/png",
        )


def test_tesseract_provider_selection_is_blocked_without_crashing() -> None:
    with pytest.raises(ValueError, match="adapter-defined but inactive"):
        get_ocr_provider("tesseract_local_candidate")


def test_tesseract_extract_request_is_not_silently_activated() -> None:
    with pytest.raises(ValueError, match="adapter-defined but inactive"):
        extract_text_from_image(
            file_bytes=b"synthetic-image",
            filename="synthetic.png",
            content_type="image/png",
            provider_name="tesseract_local_candidate",
        )
