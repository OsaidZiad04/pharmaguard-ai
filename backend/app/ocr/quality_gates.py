from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.ocr.providers import BaseOcrProvider


MAX_AVERAGE_CHARACTER_ERROR_RATE = 0.35
MAX_AVERAGE_WORD_ERROR_RATE = 0.6
MIN_AVERAGE_TOKEN_OVERLAP_SCORE = 0.45


@dataclass(frozen=True)
class OcrQualityGateResult:
    provider_name: str
    passed: bool
    failed_checks: list[str]
    warnings: list[str]
    metrics_summary: dict[str, Any]

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_provider_quality_gates(
    provider: BaseOcrProvider,
    metrics_summary: dict[str, Any],
) -> OcrQualityGateResult:
    """Evaluate prototype-safe OCR quality and provider metadata gates."""
    failed_checks: list[str] = []
    warnings: list[str] = []

    if provider.is_external_provider:
        failed_checks.append("provider_must_not_be_external_in_prototype_mode")
    if provider.requires_network:
        failed_checks.append("provider_must_not_require_network_in_prototype_mode")
    if provider.stores_images:
        failed_checks.append("provider_must_not_store_images_in_prototype_mode")

    benchmark_cases = int(metrics_summary.get("total_cases", 0))
    if benchmark_cases == 0:
        warnings.append("provider_has_no_synthetic_benchmark_cases")

    if metrics_summary.get("average_character_error_rate", 0.0) > MAX_AVERAGE_CHARACTER_ERROR_RATE:
        failed_checks.append("average_character_error_rate_exceeds_gate")
    if metrics_summary.get("average_word_error_rate", 0.0) > MAX_AVERAGE_WORD_ERROR_RATE:
        failed_checks.append("average_word_error_rate_exceeds_gate")
    if metrics_summary.get("average_token_overlap_score", 1.0) < MIN_AVERAGE_TOKEN_OVERLAP_SCORE:
        failed_checks.append("average_token_overlap_score_below_gate")
    if metrics_summary.get("medication_detection_failed", 0) > 0:
        failed_checks.append("medication_detection_hit_required")
    if metrics_summary.get("privacy_warning_failed", 0) > 0:
        failed_checks.append("privacy_warning_match_required")
    if not metrics_summary.get("output_unverified_all", True):
        failed_checks.append("ocr_output_must_remain_unverified")

    return OcrQualityGateResult(
        provider_name=provider.provider_name,
        passed=not failed_checks,
        failed_checks=failed_checks,
        warnings=warnings,
        metrics_summary=metrics_summary,
    )


def evaluate_quality_gates_for_provider_summaries(
    providers: list[BaseOcrProvider],
    provider_summaries: dict[str, dict[str, Any]],
) -> list[OcrQualityGateResult]:
    return [
        evaluate_provider_quality_gates(
            provider=provider,
            metrics_summary=provider_summaries.get(
                provider.provider_name,
                _empty_metrics_summary(provider.provider_name),
            ),
        )
        for provider in providers
    ]


def _empty_metrics_summary(provider_name: str) -> dict[str, Any]:
    return {
        "provider_name": provider_name,
        "total_cases": 0,
        "passed_cases": 0,
        "failed_cases": 0,
        "fixture_backed_cases": 0,
        "text_only_cases": 0,
        "average_character_error_rate": 0.0,
        "average_word_error_rate": 0.0,
        "average_token_overlap_score": 1.0,
        "medication_detection_failed": 0,
        "privacy_warning_failed": 0,
        "output_unverified_all": True,
    }
