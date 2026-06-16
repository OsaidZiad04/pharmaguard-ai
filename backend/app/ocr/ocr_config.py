from __future__ import annotations

from dataclasses import asdict, dataclass
import os

from app.ocr.provider_dependencies import MOCK_PROVIDER_ID


VALID_OCR_MODES = {
    "default_workflow",
    "benchmark",
    "prototype_explicit",
    "production",
}


@dataclass(frozen=True)
class OcrRuntimeConfig:
    default_provider: str
    ocr_mode: str
    enable_tesseract_prototype: bool
    allow_external_ocr: bool
    tesseract_benchmark_passed: bool
    warnings: list[str]

    def model_dump(self) -> dict:
        return asdict(self)


def get_ocr_runtime_config() -> OcrRuntimeConfig:
    warnings: list[str] = []
    default_provider = _normalize_provider_name(
        os.getenv("PHARMAGUARD_OCR_DEFAULT_PROVIDER", MOCK_PROVIDER_ID)
    )
    if default_provider != MOCK_PROVIDER_ID:
        warnings.append(
            "Non-default OCR provider configured; activation policy still applies."
        )

    ocr_mode = os.getenv("PHARMAGUARD_OCR_MODE", "default_workflow").strip().lower()
    if ocr_mode not in VALID_OCR_MODES:
        warnings.append(
            f"Invalid PHARMAGUARD_OCR_MODE={ocr_mode!r}; falling back to default_workflow."
        )
        ocr_mode = "default_workflow"

    return OcrRuntimeConfig(
        default_provider=default_provider,
        ocr_mode=ocr_mode,
        enable_tesseract_prototype=_env_bool("PHARMAGUARD_ENABLE_TESSERACT_PROTOTYPE"),
        allow_external_ocr=_env_bool("PHARMAGUARD_ALLOW_EXTERNAL_OCR"),
        tesseract_benchmark_passed=_env_bool(
            "PHARMAGUARD_TESSERACT_BENCHMARK_PASSED"
        ),
        warnings=warnings,
    )


def _env_bool(name: str) -> bool:
    value = os.getenv(name, "false").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _normalize_provider_name(provider_name: str) -> str:
    normalized = (provider_name or MOCK_PROVIDER_ID).strip().lower()
    if normalized == "mock":
        return MOCK_PROVIDER_ID
    if normalized == "synthetic_fixture":
        return "synthetic_fixture_phase_2c"
    if normalized == "tesseract":
        return "tesseract_local_candidate"
    return normalized
