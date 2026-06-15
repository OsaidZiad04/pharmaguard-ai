from app.schemas.ocr import OcrExtractedText
from app.services import ocr_service
from app.services.ocr_service import (
    MockOcrProvider,
    confirm_corrected_ocr_text,
    detect_possible_identifiers,
    extract_text_from_image,
)


def test_mock_ocr_provider_returns_unverified_output() -> None:
    result = extract_text_from_image(
        file_bytes=b"synthetic-image-bytes",
        filename="synthetic_paracetamol.png",
        content_type="image/png",
    )

    assert isinstance(result, OcrExtractedText)
    assert result.provider_name == MockOcrProvider.provider_name
    assert result.unverified_ocr_output is True
    assert result.pharmacist_review_required is True
    assert result.correction_required is True
    assert result.can_send_to_analysis is False
    assert result.confidence_score > 0
    assert "Paracetamol" in result.extracted_text


def test_possible_identifiers_are_flagged_without_confirming_pii() -> None:
    text = (
        "Patient: Synthetic Example\n"
        "DOB: 2000-01-01\n"
        "Phone: 555-010-9999\n"
        "Address: Demo Street\n"
        "Clinic: Demo Pharmacy\n"
        "National ID 1234567890"
    )

    identifiers = detect_possible_identifiers(text)

    assert "patient_name_label" in identifiers
    assert "date_of_birth_label" in identifiers
    assert "phone_number_like" in identifiers
    assert "address_label" in identifiers
    assert "clinic_label" in identifiers
    assert "national_id_like_long_number" in identifiers


def test_confirm_corrected_ocr_text_returns_privacy_warnings() -> None:
    identifiers, warnings = confirm_corrected_ocr_text(
        "Patient: Synthetic Example. Rx: Paracetamol."
    )

    assert identifiers == ["patient_name_label"]
    assert warnings
    assert warnings[0].code == "POSSIBLE_IDENTIFIER_DETECTED"


def test_ocr_service_does_not_define_external_api_client() -> None:
    assert not hasattr(ocr_service, "requests")
    assert not hasattr(ocr_service, "httpx")
