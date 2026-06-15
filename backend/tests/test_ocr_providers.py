import pytest

from app.ocr.providers import MockOcrProvider, SyntheticFixtureOcrProvider
from app.services.ocr_service import extract_text_from_image, get_ocr_provider


def test_base_provider_interface_metadata_on_mock_provider() -> None:
    provider = MockOcrProvider()

    assert provider.provider_name == "mock_ocr_phase_2a"
    assert provider.supports_content_type("image/png")
    assert provider.supports_content_type("image/jpeg")
    assert not provider.supports_content_type("application/pdf")


def test_mock_provider_does_not_require_network_or_store_images() -> None:
    provider = MockOcrProvider()

    assert provider.is_external_provider is False
    assert provider.stores_images is False
    assert provider.requires_network is False


def test_synthetic_fixture_provider_returns_deterministic_text_for_known_fixture() -> None:
    provider = SyntheticFixtureOcrProvider()

    first = provider.extract_text(
        file_bytes=b"fixture",
        filename="synthetic_paracetamol_clean.png",
        content_type="image/png",
    )
    second = provider.extract_text(
        file_bytes=b"fixture",
        filename="synthetic_paracetamol_clean.png",
        content_type="image/png",
    )

    assert first.extracted_text == second.extracted_text
    assert "Paracetamol" in first.extracted_text
    assert first.provider_name == "synthetic_fixture_phase_2c"
    assert first.is_external_provider is False
    assert first.stores_images is False
    assert first.requires_network is False


def test_synthetic_fixture_provider_supports_phase_2d_descriptors() -> None:
    provider = SyntheticFixtureOcrProvider()

    result = provider.extract_text(
        file_bytes=b"fixture descriptor",
        filename="synthetic_identifier_heavy_fake.fixture.md",
        content_type="image/png",
    )

    assert "Levothyroxine" in result.extracted_text
    assert "patient_name_label" in result.detected_possible_identifiers
    assert "phone_number_like" in result.detected_possible_identifiers


def test_unknown_fixture_falls_back_safely_to_mock_style_text() -> None:
    provider = SyntheticFixtureOcrProvider()

    result = provider.extract_text(
        file_bytes=b"fixture",
        filename="unknown_fixture.png",
        content_type="image/png",
    )

    assert result.unverified_ocr_output is True
    assert result.pharmacist_review_required is True
    assert "OCR output is unverified" in result.extracted_text


def test_provider_selection_rejects_external_provider_names() -> None:
    with pytest.raises(ValueError, match="External OCR providers"):
        get_ocr_provider("external_api")


def test_provider_selection_unknown_name_falls_back_to_mock() -> None:
    provider = get_ocr_provider("unknown_local_name")

    assert isinstance(provider, MockOcrProvider)
    assert provider.requires_network is False


def test_extract_text_from_image_uses_synthetic_fixture_provider_when_selected() -> None:
    result = extract_text_from_image(
        file_bytes=b"fixture",
        filename="synthetic_amoxicillin_possible_identifier.png",
        content_type="image/png",
        provider_name="synthetic_fixture",
    )

    assert result.provider_name == "synthetic_fixture_phase_2c"
    assert "Amoxicillin" in result.extracted_text
    assert "phone_number_like" in result.detected_possible_identifiers
