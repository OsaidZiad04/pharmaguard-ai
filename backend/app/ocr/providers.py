from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path

from app.schemas.ocr import OcrExtractedText, PrivacyWarning


SUPPORTED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}
MOCK_PROVIDER_NAME = "mock_ocr_phase_2a"
SYNTHETIC_FIXTURE_PROVIDER_NAME = "synthetic_fixture_phase_2c"


class BaseOcrProvider(ABC):
    """Provider boundary for OCR implementations.

    Current implementations are local, deterministic, and do not persist images.
    Future providers must keep OCR output unverified until pharmacist correction.
    """

    provider_name: str
    is_external_provider: bool
    stores_images: bool
    requires_network: bool
    supported_content_types: set[str] = SUPPORTED_CONTENT_TYPES

    def supports_content_type(self, content_type: str) -> bool:
        return content_type.lower() in self.supported_content_types

    @abstractmethod
    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        """Extract unverified text from an image-like payload."""


class MockOcrProvider(BaseOcrProvider):
    """Deterministic local OCR stand-in for default prototype behavior."""

    provider_name = MOCK_PROVIDER_NAME
    is_external_provider = False
    stores_images = False
    requires_network = False

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        text = _mock_text_for_filename(filename)
        return _build_ocr_result(
            provider=self,
            text=text,
            confidence_score=_mock_confidence(file_bytes, content_type),
        )


class SyntheticFixtureOcrProvider(BaseOcrProvider):
    """Filename-driven provider for approved synthetic evaluation fixtures."""

    provider_name = SYNTHETIC_FIXTURE_PROVIDER_NAME
    is_external_provider = False
    stores_images = False
    requires_network = False

    fixture_text_by_filename = {
        "synthetic_paracetamol_clean.png": (
            "Rx: Paracetamol 500 mg tablets. Pharmacist must verify directions."
        ),
        "synthetic_ibuprofen_noisy.png": (
            "Patient: Synthetic Example. Rx: Ibuprofen tabiets. Pharmacist revlew required."
        ),
        "synthetic_amoxicillin_possible_identifier.png": (
            "Phone: 555-010-2222. Rx: Amoxicillin capsules. Confirm allergy status."
        ),
        "synthetic_no_medication.png": (
            "Image text unreadable. Ask pharmacist to review source image and re-enter prescription text."
        ),
    }

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        text = self.fixture_text_by_filename.get(
            Path(filename).name.lower(),
            _mock_text_for_filename(filename),
        )
        return _build_ocr_result(
            provider=self,
            text=text,
            confidence_score=_fixture_confidence(file_bytes, filename),
        )


def detect_possible_identifiers(text: str) -> list[str]:
    """Return possible identifier categories without validating or exposing values."""
    possible_identifiers: list[str] = []
    normalized_text = text or ""

    for identifier_type, pattern in IDENTIFIER_PATTERNS:
        if pattern.search(normalized_text) and identifier_type not in possible_identifiers:
            possible_identifiers.append(identifier_type)

    return possible_identifiers


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


def _build_ocr_result(
    provider: BaseOcrProvider,
    text: str,
    confidence_score: float,
) -> OcrExtractedText:
    detected_identifiers = detect_possible_identifiers(text)
    return OcrExtractedText(
        extracted_text=text,
        confidence_score=confidence_score,
        provider_name=provider.provider_name,
        is_external_provider=provider.is_external_provider,
        stores_images=provider.stores_images,
        requires_network=provider.requires_network,
        supported_content_types=sorted(provider.supported_content_types),
        unverified_ocr_output=True,
        pharmacist_review_required=True,
        privacy_warnings=build_privacy_warnings(detected_identifiers),
        detected_possible_identifiers=detected_identifiers,
        correction_required=True,
        can_send_to_analysis=False,
    )


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


def _fixture_confidence(file_bytes: bytes, filename: str) -> float:
    if not file_bytes:
        return 0.0
    if Path(filename).name.lower() in SyntheticFixtureOcrProvider.fixture_text_by_filename:
        return 0.82
    return 0.68


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
