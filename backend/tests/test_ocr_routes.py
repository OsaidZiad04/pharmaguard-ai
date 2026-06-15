from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_supported_image_upload_returns_unverified_ocr_output() -> None:
    response = client.post(
        "/ocr/extract-image",
        files={"file": ("synthetic_paracetamol.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_name"] == "mock_ocr_phase_2a"
    assert payload["is_external_provider"] is False
    assert payload["stores_images"] is False
    assert payload["requires_network"] is False
    assert "image/png" in payload["supported_content_types"]
    assert payload["unverified_ocr_output"] is True
    assert payload["pharmacist_review_required"] is True
    assert payload["correction_required"] is True
    assert payload["can_send_to_analysis"] is False
    assert "extracted_medications" not in payload


def test_unsupported_file_type_is_rejected() -> None:
    response = client.post(
        "/ocr/extract-image",
        files={"file": ("synthetic.txt", b"not-an-image", "text/plain")},
    )

    assert response.status_code == 415
    assert "Unsupported OCR upload type" in response.text


def test_oversized_upload_is_rejected() -> None:
    response = client.post(
        "/ocr/extract-image",
        files={"file": ("large.png", b"x" * (5 * 1024 * 1024 + 1), "image/png")},
    )

    assert response.status_code == 413


def test_possible_identifiers_are_returned_as_privacy_warnings() -> None:
    response = client.post(
        "/ocr/extract-image",
        files={"file": ("identifier_case.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "patient_name_label" in payload["detected_possible_identifiers"]
    assert payload["privacy_warnings"]
    assert payload["privacy_warnings"][0]["code"] == "POSSIBLE_IDENTIFIER_DETECTED"


def test_synthetic_fixture_provider_route_returns_provider_metadata() -> None:
    response = client.post(
        "/ocr/extract-image?provider_name=synthetic_fixture",
        files={
            "file": (
                "synthetic_amoxicillin_possible_identifier.png",
                b"fake-image",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_name"] == "synthetic_fixture_phase_2c"
    assert payload["is_external_provider"] is False
    assert payload["stores_images"] is False
    assert payload["requires_network"] is False
    assert "Amoxicillin" in payload["extracted_text"]


def test_confirm_text_endpoint_returns_corrected_text_for_analysis() -> None:
    response = client.post(
        "/ocr/confirm-text",
        json={
            "extracted_text": "Synthetic OCR draft with spelling issues.",
            "corrected_text": "Rx: Paracetamol 500 mg tablets. Pharmacist-corrected synthetic text.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["corrected_text"].startswith("Rx: Paracetamol")
    assert payload["pharmacist_review_required"] is True
    assert payload["correction_required"] is False
    assert payload["can_send_to_analysis"] is True
    assert payload["correction_audit"]["changed"] is True
    assert payload["correction_audit"]["pharmacist_review_required"] is True
    assert "paracetamol" in payload["correction_audit"]["detected_medication_terms"]


def test_ocr_confirm_text_does_not_trigger_prescription_analysis() -> None:
    response = client.post(
        "/ocr/confirm-text",
        json={
            "extracted_text": "OCR text",
            "corrected_text": "Rx: Paracetamol 500 mg tablets.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "extracted_medications" not in payload
    assert "grounded_answer" not in payload
    assert "correction_audit" in payload
    assert "retrieved_chunks" not in payload


def test_external_provider_name_is_rejected_without_network_call() -> None:
    response = client.post(
        "/ocr/extract-image?provider_name=external_api",
        files={"file": ("synthetic.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 400
    assert "External OCR providers are not enabled" in response.text


def test_tesseract_provider_request_is_rejected_without_activation() -> None:
    response = client.post(
        "/ocr/extract-image?provider_name=tesseract_local_candidate",
        files={"file": ("synthetic.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 400
    assert "adapter-defined but inactive" in response.text


def test_confirm_text_endpoint_keeps_possible_identifier_warnings() -> None:
    response = client.post(
        "/ocr/confirm-text",
        json={
            "extracted_text": "Patient: Synthetic Example. Rx: Paracetamol tablets.",
            "corrected_text": "Rx: Paracetamol tablets.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "patient_name_label" in payload["detected_possible_identifiers"]
    assert payload["privacy_warnings"]
    assert payload["correction_audit"]["privacy_warnings"]
