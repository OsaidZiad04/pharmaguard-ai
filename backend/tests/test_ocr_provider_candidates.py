from app.ocr.provider_candidates import (
    candidate_allowed_in_prototype,
    get_provider_candidate,
    list_provider_candidates,
    summarize_candidate_readiness,
)


def test_candidate_registry_loads_expected_candidates() -> None:
    candidates = list_provider_candidates()
    candidate_ids = {candidate.provider_id for candidate in candidates}

    assert len(candidates) == 5
    assert {
        "mock_ocr_phase_2a",
        "synthetic_fixture_phase_2c",
        "tesseract_local_candidate",
        "easyocr_local_candidate",
        "cloud_ocr_candidate_placeholder",
    } == candidate_ids


def test_implemented_candidates_are_prototype_allowed() -> None:
    mock = get_provider_candidate("mock_ocr_phase_2a")
    synthetic = get_provider_candidate("synthetic_fixture_phase_2c")

    assert mock is not None
    assert synthetic is not None
    assert candidate_allowed_in_prototype(mock) is True
    assert candidate_allowed_in_prototype(synthetic) is True


def test_cloud_candidate_is_not_prototype_allowed() -> None:
    cloud = get_provider_candidate("cloud_ocr_candidate_placeholder")

    assert cloud is not None
    assert cloud.requires_network is True
    assert cloud.stores_images is True
    assert candidate_allowed_in_prototype(cloud) is False


def test_planned_local_candidates_are_not_activated_accidentally() -> None:
    tesseract = get_provider_candidate("tesseract_local_candidate")
    easyocr = get_provider_candidate("easyocr_local_candidate")

    assert tesseract is not None
    assert easyocr is not None
    assert tesseract.current_status == "planned"
    assert easyocr.current_status == "planned"
    assert candidate_allowed_in_prototype(tesseract) is False
    assert candidate_allowed_in_prototype(easyocr) is False


def test_candidate_readiness_summary_includes_blockers() -> None:
    candidate = get_provider_candidate("easyocr_local_candidate")

    assert candidate is not None
    summary = summarize_candidate_readiness(candidate)

    assert summary["prototype_allowed"] is False
    assert "Provider is metadata-only and is not active." in summary["integration_blockers"]
    assert "Model downloads are disallowed in this phase." in summary["integration_blockers"]
