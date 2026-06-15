from __future__ import annotations

from datetime import datetime, timezone

from app.ocr.evaluation import (
    character_error_rate,
    token_overlap_score,
    word_error_rate,
)
from app.schemas.ocr import OcrCorrectionAudit, OcrCorrectionDiff
from app.services.extraction_service import extract_medication_candidates
from app.services.ocr_service import build_privacy_warnings, detect_possible_identifiers


def build_ocr_correction_audit(
    original_ocr_text: str,
    corrected_text: str,
) -> OcrCorrectionAudit:
    original = original_ocr_text or ""
    corrected = corrected_text.strip()
    changed = original.strip() != corrected
    cer = character_error_rate(corrected, original)
    wer = word_error_rate(corrected, original)
    overlap = token_overlap_score(corrected, original)
    detected_identifiers = _combined_possible_identifiers(original, corrected)

    return OcrCorrectionAudit(
        original_ocr_text=original,
        corrected_text=corrected,
        changed=changed,
        change_summary=_change_summary(changed, cer, wer),
        diff=OcrCorrectionDiff(
            changed=changed,
            character_error_rate=cer,
            word_error_rate=wer,
            token_overlap_score=overlap,
        ),
        character_error_rate=cer,
        word_error_rate=wer,
        detected_medication_terms=_detected_medication_terms(corrected),
        privacy_warnings=build_privacy_warnings(detected_identifiers),
        detected_possible_identifiers=detected_identifiers,
        pharmacist_review_required=True,
        can_send_to_analysis=True,
        generated_at=_utc_now(),
    )


def _detected_medication_terms(text: str) -> list[str]:
    candidates = extract_medication_candidates(text)
    return sorted({candidate["name"] for candidate in candidates})


def _combined_possible_identifiers(original: str, corrected: str) -> list[str]:
    identifiers = {
        *detect_possible_identifiers(original),
        *detect_possible_identifiers(corrected),
    }
    return sorted(identifiers)


def _change_summary(changed: bool, cer: float, wer: float) -> str:
    if not changed:
        return "No OCR correction changes recorded."
    return (
        "OCR text was corrected by pharmacist review "
        f"(character error rate {cer:.2f}, word error rate {wer:.2f})."
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
