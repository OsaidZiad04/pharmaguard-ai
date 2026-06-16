from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from app.ocr.ocr_config import (
    OcrRuntimeConfig,
    get_ocr_runtime_config,
)
from app.ocr.provider_dependencies import (
    MOCK_PROVIDER_ID,
    SYNTHETIC_FIXTURE_PROVIDER_ID,
    TESSERACT_PROVIDER_ID,
    ProviderDependencyStatus,
    get_provider_dependency_status,
)
from app.ocr.providers import MockOcrProvider, SyntheticFixtureOcrProvider
from app.ocr.local_tesseract_provider import TesseractLocalOcrProvider


OcrMode = Literal["default_workflow", "benchmark", "prototype_explicit", "production"]
CLOUD_PROVIDER_ID = "cloud_ocr_candidate_placeholder"


@dataclass(frozen=True)
class OcrProviderActivationResult:
    provider_id: str
    mode: str
    allowed: bool
    correction_gate_required: bool
    default_provider: bool
    production_allowed: bool
    blocking_reasons: list[str]
    warnings: list[str]

    def model_dump(self) -> dict:
        return asdict(self)


def get_ocr_activation_policy(provider_id: str) -> dict:
    provider_id = normalize_provider_id(provider_id)
    if provider_id == MOCK_PROVIDER_ID:
        return {
            "provider_id": provider_id,
            "allowed_modes": ["default_workflow", "benchmark", "prototype_explicit"],
            "production_allowed": False,
            "correction_gate_required": True,
            "default_provider_allowed": True,
        }
    if provider_id == SYNTHETIC_FIXTURE_PROVIDER_ID:
        return {
            "provider_id": provider_id,
            "allowed_modes": ["default_workflow", "benchmark", "prototype_explicit"],
            "production_allowed": False,
            "correction_gate_required": True,
            "default_provider_allowed": False,
        }
    if provider_id == TESSERACT_PROVIDER_ID:
        return {
            "provider_id": provider_id,
            "allowed_modes": ["benchmark", "prototype_explicit"],
            "production_allowed": False,
            "correction_gate_required": True,
            "default_provider_allowed": False,
        }
    return {
        "provider_id": provider_id,
        "allowed_modes": [],
        "production_allowed": False,
        "correction_gate_required": True,
        "default_provider_allowed": False,
    }


def evaluate_ocr_provider_activation(
    provider_id: str,
    mode: str,
    config: OcrRuntimeConfig | None = None,
    dependency_status: ProviderDependencyStatus | None = None,
    benchmark_gate_passed: bool | None = None,
) -> OcrProviderActivationResult:
    config = config or get_ocr_runtime_config()
    provider_id = normalize_provider_id(provider_id)
    mode = normalize_ocr_mode(mode)
    dependency_status = dependency_status or get_provider_dependency_status(provider_id)
    benchmark_gate_passed = (
        config.tesseract_benchmark_passed
        if benchmark_gate_passed is None
        else benchmark_gate_passed
    )
    blocking_reasons: list[str] = []
    warnings = list(config.warnings)

    if provider_id == CLOUD_PROVIDER_ID or _looks_external_provider(provider_id):
        blocking_reasons.append("External/cloud OCR providers are blocked.")
        if not config.allow_external_ocr:
            blocking_reasons.append("PHARMAGUARD_ALLOW_EXTERNAL_OCR is false.")
        return _result(provider_id, mode, config, blocking_reasons, warnings)

    if provider_id == MOCK_PROVIDER_ID:
        if mode == "production":
            blocking_reasons.append("Mock OCR is not production validated.")
        return _result(provider_id, mode, config, blocking_reasons, warnings)

    if provider_id == SYNTHETIC_FIXTURE_PROVIDER_ID:
        warnings.append("Synthetic fixture provider is for synthetic evaluation only.")
        if mode == "production":
            blocking_reasons.append("Synthetic fixture OCR is not production validated.")
        return _result(provider_id, mode, config, blocking_reasons, warnings)

    if provider_id == TESSERACT_PROVIDER_ID:
        provider = TesseractLocalOcrProvider()
        if provider.is_external_provider or provider.requires_network or provider.stores_images:
            blocking_reasons.append(
                "Tesseract provider metadata must remain local, non-networked, and non-storing."
            )
        if mode == "default_workflow":
            blocking_reasons.append("Tesseract is blocked in default_workflow mode.")
        elif mode == "benchmark":
            if not dependency_status.available:
                blocking_reasons.append(
                    "Tesseract benchmark requires available local dependencies."
                )
        elif mode == "prototype_explicit":
            if not config.enable_tesseract_prototype:
                blocking_reasons.append(
                    "PHARMAGUARD_ENABLE_TESSERACT_PROTOTYPE is false."
                )
            if not dependency_status.available:
                blocking_reasons.append(
                    "Tesseract prototype mode requires available local dependencies."
                )
            if not benchmark_gate_passed:
                blocking_reasons.append(
                    "Tesseract prototype mode requires a recorded passing synthetic benchmark."
                )
        elif mode == "production":
            blocking_reasons.append("Tesseract is not production allowed.")
        if benchmark_gate_passed:
            warnings.append(
                "Synthetic OCR benchmark pass is engineering validation only, not clinical validation."
            )
        return _result(provider_id, mode, config, blocking_reasons, warnings)

    blocking_reasons.append("Unknown OCR provider is blocked by activation policy.")
    return _result(provider_id, mode, config, blocking_reasons, warnings)


def is_provider_allowed_for_mode(provider_id: str, mode: str) -> bool:
    return evaluate_ocr_provider_activation(provider_id, mode).allowed


def require_correction_gate(provider_id: str) -> bool:
    return get_ocr_activation_policy(provider_id)["correction_gate_required"]


def normalize_provider_id(provider_id: str | None) -> str:
    normalized = (provider_id or MOCK_PROVIDER_ID).strip().lower()
    aliases = {
        "mock": MOCK_PROVIDER_ID,
        "synthetic_fixture": SYNTHETIC_FIXTURE_PROVIDER_ID,
        "tesseract": TESSERACT_PROVIDER_ID,
        "cloud": CLOUD_PROVIDER_ID,
        "external": CLOUD_PROVIDER_ID,
        "external_api": CLOUD_PROVIDER_ID,
    }
    return aliases.get(normalized, normalized)


def normalize_ocr_mode(mode: str | None) -> str:
    normalized = (mode or "default_workflow").strip().lower()
    if normalized not in {
        "default_workflow",
        "benchmark",
        "prototype_explicit",
        "production",
    }:
        return "default_workflow"
    return normalized


def _result(
    provider_id: str,
    mode: str,
    config: OcrRuntimeConfig,
    blocking_reasons: list[str],
    warnings: list[str],
) -> OcrProviderActivationResult:
    return OcrProviderActivationResult(
        provider_id=provider_id,
        mode=mode,
        allowed=not blocking_reasons,
        correction_gate_required=True,
        default_provider=provider_id == config.default_provider,
        production_allowed=False,
        blocking_reasons=sorted(set(blocking_reasons)),
        warnings=sorted(set(warnings)),
    )


def _looks_external_provider(provider_id: str) -> bool:
    return provider_id in {
        "google_vision",
        "azure_ocr",
        "aws_textract",
        "cloud_ocr_candidate_placeholder",
    }
