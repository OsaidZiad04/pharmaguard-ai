from app.ocr.provider_candidates import get_provider_candidate
from app.ocr.provider_swap_readiness import assess_provider_swap_readiness


def test_readiness_allows_current_implemented_providers_for_prototype() -> None:
    for provider_id in ["mock_ocr_phase_2a", "synthetic_fixture_phase_2c"]:
        candidate = get_provider_candidate(provider_id)
        assert candidate is not None

        readiness = assess_provider_swap_readiness(candidate)

        assert readiness.ready_for_prototype is True
        assert readiness.blocking_reasons == []


def test_readiness_blocks_networked_provider_in_prototype() -> None:
    candidate = get_provider_candidate("cloud_ocr_candidate_placeholder")
    assert candidate is not None

    readiness = assess_provider_swap_readiness(candidate)

    assert readiness.ready_for_prototype is False
    assert "Networked OCR providers are blocked in prototype mode." in readiness.blocking_reasons
    assert "Image-storing OCR providers are blocked in prototype mode." in readiness.blocking_reasons
    assert "Complete formal privacy and security review." in readiness.required_next_steps


def test_readiness_blocks_image_storing_provider_in_prototype() -> None:
    candidate = get_provider_candidate("cloud_ocr_candidate_placeholder")
    assert candidate is not None

    readiness = assess_provider_swap_readiness(candidate)

    assert readiness.ready_for_prototype is False
    assert "Image-storing OCR providers are blocked in prototype mode." in readiness.blocking_reasons


def test_readiness_marks_planned_local_candidate_for_future_evaluation_only() -> None:
    candidate = get_provider_candidate("tesseract_local_candidate")
    assert candidate is not None

    readiness = assess_provider_swap_readiness(candidate)

    assert readiness.ready_for_prototype is False
    assert readiness.ready_for_future_evaluation is True
    assert "Provider is not implemented in the current codebase." in readiness.blocking_reasons
    assert "Provider does not expose an active BaseOcrProvider adapter." in readiness.blocking_reasons


def test_readiness_keeps_model_download_candidate_out_of_prototype() -> None:
    candidate = get_provider_candidate("easyocr_local_candidate")
    assert candidate is not None

    readiness = assess_provider_swap_readiness(candidate)

    assert readiness.ready_for_prototype is False
    assert "Provider requires model download/cache review." in readiness.warnings
    assert "Define model cache location and offline install policy." in readiness.required_next_steps
