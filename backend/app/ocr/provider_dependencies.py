from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.util import find_spec
from shutil import which


TESSERACT_PROVIDER_ID = "tesseract_local_candidate"
MOCK_PROVIDER_ID = "mock_ocr_phase_2a"
SYNTHETIC_FIXTURE_PROVIDER_ID = "synthetic_fixture_phase_2c"


@dataclass(frozen=True)
class ProviderDependencyStatus:
    provider_id: str
    available: bool
    python_package_available: bool | None
    system_binary_available: bool | None
    checked_dependencies: list[str]
    details: str

    def model_dump(self) -> dict:
        return asdict(self)


def check_python_package_available(package_name: str) -> bool:
    """Check whether an optional Python package is importable without importing it."""
    return find_spec(package_name) is not None


def check_tesseract_available() -> bool:
    """Check whether a local Tesseract binary appears to be available."""
    return which("tesseract") is not None


def get_provider_dependency_status(provider_id: str) -> ProviderDependencyStatus:
    normalized_id = provider_id.strip().lower()

    if normalized_id in {MOCK_PROVIDER_ID, SYNTHETIC_FIXTURE_PROVIDER_ID}:
        return ProviderDependencyStatus(
            provider_id=normalized_id,
            available=True,
            python_package_available=None,
            system_binary_available=None,
            checked_dependencies=[],
            details="No optional OCR engine dependencies are required.",
        )

    if normalized_id == TESSERACT_PROVIDER_ID:
        pytesseract_available = check_python_package_available("pytesseract")
        pillow_available = check_python_package_available("PIL")
        python_package_available = pytesseract_available and pillow_available
        system_binary_available = check_tesseract_available()
        available = python_package_available and system_binary_available
        missing_dependencies = [
            dependency_name
            for dependency_name, dependency_available in [
                ("pytesseract", pytesseract_available),
                ("Pillow", pillow_available),
                ("tesseract_binary", system_binary_available),
            ]
            if not dependency_available
        ]
        details = (
            "pytesseract, Pillow, and local tesseract binary detected."
            if available
            else "Missing optional local dependency/dependencies: "
            f"{', '.join(missing_dependencies)} not detected."
        )
        return ProviderDependencyStatus(
            provider_id=normalized_id,
            available=available,
            python_package_available=python_package_available,
            system_binary_available=system_binary_available,
            checked_dependencies=["pytesseract", "Pillow", "tesseract_binary"],
            details=details,
        )

    return ProviderDependencyStatus(
        provider_id=normalized_id,
        available=False,
        python_package_available=None,
        system_binary_available=None,
        checked_dependencies=[],
        details="No dependency check is defined for this OCR provider candidate.",
    )
