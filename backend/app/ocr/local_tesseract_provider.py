from __future__ import annotations

from app.ocr.provider_dependencies import (
    TESSERACT_PROVIDER_ID,
    ProviderDependencyStatus,
    get_provider_dependency_status,
)
from app.ocr.providers import BaseOcrProvider
from app.schemas.ocr import OcrExtractedText


class ProviderUnavailableError(RuntimeError):
    """Raised when an optional OCR adapter is intentionally unavailable."""


class TesseractLocalOcrProvider(BaseOcrProvider):
    """Disabled-by-default adapter skeleton for a future local Tesseract provider."""

    provider_name = TESSERACT_PROVIDER_ID
    is_external_provider = False
    stores_images = False
    requires_network = False
    requires_system_dependency = True
    requires_model_download = False
    enabled_by_default = False
    prototype_allowed = False

    def dependency_status(self) -> ProviderDependencyStatus:
        return get_provider_dependency_status(self.provider_name)

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        dependency_status = self.dependency_status()
        if not self.enabled_by_default or not self.prototype_allowed:
            raise ProviderUnavailableError(
                "Tesseract local OCR adapter is disabled by default and is not "
                "prototype-allowed in Phase 2F."
            )
        if not dependency_status.available:
            raise ProviderUnavailableError(
                "Tesseract local OCR dependencies are unavailable. "
                f"{dependency_status.details}"
            )
        raise ProviderUnavailableError(
            "Tesseract local OCR extraction is not activated in Phase 2F."
        )
