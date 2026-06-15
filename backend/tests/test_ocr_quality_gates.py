from app.ocr.providers import BaseOcrProvider, MockOcrProvider
from app.ocr.quality_gates import evaluate_provider_quality_gates
from app.schemas.ocr import OcrExtractedText


def test_quality_gates_pass_for_safe_provider_with_current_metrics() -> None:
    result = evaluate_provider_quality_gates(
        provider=MockOcrProvider(),
        metrics_summary=_metrics_summary(),
    )

    assert result.passed is True
    assert result.failed_checks == []


def test_quality_gates_fail_when_metrics_exceed_thresholds() -> None:
    result = evaluate_provider_quality_gates(
        provider=MockOcrProvider(),
        metrics_summary=_metrics_summary(
            average_character_error_rate=0.9,
            average_word_error_rate=0.9,
            average_token_overlap_score=0.1,
        ),
    )

    assert result.passed is False
    assert "average_character_error_rate_exceeds_gate" in result.failed_checks
    assert "average_word_error_rate_exceeds_gate" in result.failed_checks
    assert "average_token_overlap_score_below_gate" in result.failed_checks


def test_quality_gates_fail_when_required_checks_are_missing() -> None:
    result = evaluate_provider_quality_gates(
        provider=MockOcrProvider(),
        metrics_summary=_metrics_summary(
            medication_detection_failed=1,
            privacy_warning_failed=1,
            output_unverified_all=False,
        ),
    )

    assert result.passed is False
    assert "medication_detection_hit_required" in result.failed_checks
    assert "privacy_warning_match_required" in result.failed_checks
    assert "ocr_output_must_remain_unverified" in result.failed_checks


def test_quality_gates_fail_for_network_provider() -> None:
    result = evaluate_provider_quality_gates(
        provider=_UnsafeProvider(requires_network=True),
        metrics_summary=_metrics_summary(),
    )

    assert result.passed is False
    assert "provider_must_not_require_network_in_prototype_mode" in result.failed_checks


def test_quality_gates_fail_for_image_storing_provider() -> None:
    result = evaluate_provider_quality_gates(
        provider=_UnsafeProvider(stores_images=True),
        metrics_summary=_metrics_summary(),
    )

    assert result.passed is False
    assert "provider_must_not_store_images_in_prototype_mode" in result.failed_checks


def test_quality_gates_fail_for_external_provider() -> None:
    result = evaluate_provider_quality_gates(
        provider=_UnsafeProvider(is_external_provider=True),
        metrics_summary=_metrics_summary(),
    )

    assert result.passed is False
    assert "provider_must_not_be_external_in_prototype_mode" in result.failed_checks


def _metrics_summary(**overrides):
    summary = {
        "provider_name": "mock_ocr_phase_2a",
        "total_cases": 5,
        "passed_cases": 5,
        "failed_cases": 0,
        "fixture_backed_cases": 0,
        "text_only_cases": 5,
        "average_character_error_rate": 0.1,
        "average_word_error_rate": 0.2,
        "average_token_overlap_score": 0.8,
        "medication_detection_failed": 0,
        "privacy_warning_failed": 0,
        "output_unverified_all": True,
    }
    summary.update(overrides)
    return summary


class _UnsafeProvider(BaseOcrProvider):
    provider_name = "unsafe_test_provider"
    is_external_provider = False
    stores_images = False
    requires_network = False

    def __init__(
        self,
        *,
        is_external_provider: bool = False,
        stores_images: bool = False,
        requires_network: bool = False,
    ) -> None:
        self.is_external_provider = is_external_provider
        self.stores_images = stores_images
        self.requires_network = requires_network

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        raise NotImplementedError
