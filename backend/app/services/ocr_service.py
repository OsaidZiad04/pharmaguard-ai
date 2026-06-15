from __future__ import annotations

import re
from abc import ABC, abstractmethod

from app.schemas.ocr import OcrExtractedText, PrivacyWarning


PROVIDER_NAME = "mock_ocr_phase_2a"


class BaseOcrProvider(ABC):
    """Provider boundary for future OCR implementations.

    Implementations must not persist prescription images by default and must
    keep OCR output marked unverified until a pharmacist corrects it.
    """

    provider_name: str

    @abstractmethod
    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        """Extract unverified text from an image-like payload."""


class MockOcrProvider(BaseOcrProvider):
    """Deterministic local OCR stand-in for Phase 2A tests and demos."""

    provider_name = PROVIDER_NAME

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        text = _mock_text_for_filename(filename)
        detected_identifiers = detect_possible_identifiers(text)

        return OcrExtractedText(
            extracted_text=text,
            confidence_score=_mock_confidence(file_bytes, content_type),
            provider_name=self.provider_name,
            unverified_ocr_output=True,
            pharmacist_review_required=True,
            privacy_warnings=build_privacy_warnings(detected_identifiers),
            detected_possible_identifiers=detected_identifiers,
            correction_required=True,
            can_send_to_analysis=False,
        )


def extract_text_from_image(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    provider: BaseOcrProvider | None = None,
) -> OcrExtractedText:
    """Run the configured local OCR provider without external API calls."""
    ocr_provider = provider or MockOcrProvider()
    return ocr_provider.extract_text(file_bytes, filename, content_type)


def confirm_corrected_ocr_text(corrected_text: str) -> tuple[list[str], list[PrivacyWarning]]:
    """Validate pharmacist-corrected text for privacy warnings before analysis."""
    detected_identifiers = detect_possible_identifiers(corrected_text)
    return detected_identifiers, build_privacy_warnings(detected_identifiers)


def detect_possible_identifiers(text: str) -> list[str]:
    """Return possible identifier categories without validating or exposing values."""
    possible_identifiers: list[str] = []
    normalized_text = text or ""

    for identifier_type, pattern in IDENTIFIER_PATTERNS:
        if pattern.search(normalized_text) and identifier_type not in possible_identifiers:
            possible_identifiers.append(identifier_type)

    return possible_identifiers


def _mock_text_for_filename(filename: str) -> str:
    normalized_filename = filename.lower()
    if "identifier" in normalized_filename or "privacy" in normalized_filename:
        return (
            "Patient: Synthetic Example\n"
            "DOB: 2000-01-01\n"
            "Phone: 555-010-9999\n"
            "Clinic: Demo Pharmacy\n"
            "Rx: Paracetamol 500 mg tablets. Pharmacist must verify OCR text."
        )
    if "amoxicillin" in normalized_filename:
        return (
            "Synthetic OCR draft: Amoxicillin capsules. "
            "Directions are unclear and require pharmacist correction."
        )
    if "ibuprofen" in normalized_filename:
        return (
            "Synthetic OCR draft: Ibuprofen tablets. "
            "Pharmacist must verify strength, directions, and patient context."
        )
    return (
        "Synthetic OCR draft: Paracetamol 500 mg tablets. "
        "OCR output is unverified and requires pharmacist correction before analysis."
    )


def _mock_confidence(file_bytes: bytes, content_type: str) -> float:
    if not file_bytes:
        return 0.0
    if content_type == "image/webp":
        return 0.72
    return 0.76


def build_privacy_warnings(possible_identifiers: list[str]) -> list[PrivacyWarning]:
    return [
        PrivacyWarning(
            code="POSSIBLE_IDENTIFIER_DETECTED",
            severity="warning",
            message=(
                f"Possible identifier pattern detected: {identifier_type}. "
                "Treat OCR text as unverified and review privacy before analysis."
            ),
        )
        for identifier_type in possible_identifiers
    ]


IDENTIFIER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "phone_number_like",
        re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}"),
    ),
    ("national_id_like_long_number", re.compile(r"\b\d{8,}\b")),
    ("patient_name_label", re.compile(r"\bPatient\s*:", flags=re.IGNORECASE)),
    ("address_label", re.compile(r"\bAddress\s*:", flags=re.IGNORECASE)),
    ("clinic_label", re.compile(r"\bClinic\s*:", flags=re.IGNORECASE)),
    (
        "date_of_birth_label",
        re.compile(r"\b(?:DOB|Date\s+of\s+Birth)\s*:", flags=re.IGNORECASE),
    ),
]
