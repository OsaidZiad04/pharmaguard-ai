from __future__ import annotations

from io import BytesIO
from statistics import mean

from app.ocr.provider_dependencies import (
    TESSERACT_PROVIDER_ID,
    ProviderDependencyStatus,
    get_provider_dependency_status,
)
from app.ocr.providers import BaseOcrProvider, _build_ocr_result
from app.schemas.ocr import OcrExtractedText


class ProviderUnavailableError(RuntimeError):
    """Raised when an optional OCR adapter is intentionally unavailable."""


class TesseractLocalOcrProvider(BaseOcrProvider):
    """Disabled-by-default local Tesseract adapter for explicit benchmarks only."""

    provider_name = TESSERACT_PROVIDER_ID
    is_external_provider = False
    stores_images = False
    requires_network = False
    requires_system_dependency = True
    requires_model_download = False
    enabled_by_default = False
    prototype_allowed = False
    benchmark_only = True

    def __init__(
        self,
        benchmark_mode: bool = False,
        explicitly_enabled: bool = False,
    ) -> None:
        self.benchmark_mode = benchmark_mode
        self.explicitly_enabled = explicitly_enabled

    def dependency_status(self) -> ProviderDependencyStatus:
        return get_provider_dependency_status(self.provider_name)

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        dependency_status = self.dependency_status()
        if not (self.benchmark_mode or self.explicitly_enabled):
            raise ProviderUnavailableError(
                "Tesseract local OCR adapter is disabled by default and is not "
                "available outside explicit benchmark mode."
            )
        if not dependency_status.available:
            raise ProviderUnavailableError(
                "Tesseract local OCR dependencies are unavailable. "
                f"{dependency_status.details}"
            )
        if not self.supports_content_type(content_type):
            raise ProviderUnavailableError(
                f"Tesseract local OCR does not support content type: {content_type}"
            )

        try:
            from PIL import Image
            import pytesseract
        except ImportError as error:
            raise ProviderUnavailableError(
                "Tesseract local OCR Python dependencies are unavailable at runtime."
            ) from error

        try:
            with Image.open(BytesIO(file_bytes)) as image:
                prepared_image = image.convert("RGB")
                extracted_text = pytesseract.image_to_string(prepared_image).strip()
                confidence_score = _extract_tesseract_confidence(
                    pytesseract_module=pytesseract,
                    image=prepared_image,
                    extracted_text=extracted_text,
                )
        except Exception as error:
            raise ProviderUnavailableError(
                "Tesseract local OCR extraction failed safely during benchmark mode. "
                f"{error}"
            ) from error

        return _build_ocr_result(
            provider=self,
            text=extracted_text,
            confidence_score=confidence_score,
        )


def _extract_tesseract_confidence(
    pytesseract_module,
    image,
    extracted_text: str,
) -> float:
    try:
        data = pytesseract_module.image_to_data(
            image,
            output_type=pytesseract_module.Output.DICT,
        )
        confidence_values: list[float] = []
        for raw_confidence in data.get("conf", []):
            try:
                value = float(raw_confidence)
            except (TypeError, ValueError):
                continue
            if value >= 0:
                confidence_values.append(value)
        if confidence_values:
            return round(mean(confidence_values) / 100, 4)
    except Exception:
        pass
    return 0.5 if extracted_text else 0.0
