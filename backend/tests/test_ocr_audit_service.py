from app.services.ocr_audit_service import build_ocr_correction_audit


def test_correction_audit_detects_unchanged_text() -> None:
    text = "Rx: Paracetamol tablets. Pharmacist review required."
    audit = build_ocr_correction_audit(
        original_ocr_text=text,
        corrected_text=text,
    )

    assert audit.changed is False
    assert audit.diff.changed is False
    assert audit.character_error_rate == 0.0
    assert audit.word_error_rate == 0.0
    assert audit.detected_medication_terms == ["paracetamol"]
    assert audit.pharmacist_review_required is True
    assert audit.can_send_to_analysis is True


def test_correction_audit_detects_changed_text_and_privacy_warnings() -> None:
    audit = build_ocr_correction_audit(
        original_ocr_text="Patient: Synthetic Example. Rx: Paracetmol tabiets.",
        corrected_text="Rx: Paracetamol tablets.",
    )

    assert audit.changed is True
    assert audit.diff.changed is True
    assert audit.character_error_rate > 0
    assert audit.word_error_rate > 0
    assert audit.detected_medication_terms == ["paracetamol"]
    assert "patient_name_label" in audit.detected_possible_identifiers
    assert audit.privacy_warnings
    assert audit.pharmacist_review_required is True
