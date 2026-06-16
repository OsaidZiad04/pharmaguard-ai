from pathlib import Path
import subprocess
import sys

import pytest

from app.ocr.local_tesseract_provider import (
    ProviderUnavailableError,
    TesseractLocalOcrProvider,
)
from app.ocr.provider_dependencies import (
    TESSERACT_PROVIDER_ID,
    ProviderDependencyStatus,
    get_provider_dependency_status,
)
from app.ocr.tesseract_benchmark import (
    evaluate_tesseract_case,
    load_tesseract_benchmark_cases,
    run_tesseract_benchmark,
)
from app.schemas.ocr import OcrExtractedText


def test_tesseract_benchmark_cases_use_only_synthetic_fixture_inputs() -> None:
    case_groups = load_tesseract_benchmark_cases()

    assert len(case_groups["image_cases"]) >= 6
    assert case_groups["skipped_descriptor_cases"]
    assert all(
        case["fixture_filename"].endswith((".png", ".jpg", ".jpeg", ".webp"))
        for case in case_groups["image_cases"]
    )
    assert all(
        skipped["fixture_filename"].endswith(".fixture.md")
        for skipped in case_groups["skipped_descriptor_cases"]
    )


def test_tesseract_benchmark_handles_unavailable_dependencies_gracefully() -> None:
    dependency_status = ProviderDependencyStatus(
        provider_id=TESSERACT_PROVIDER_ID,
        available=False,
        python_package_available=False,
        system_binary_available=False,
        checked_dependencies=["pytesseract", "Pillow", "tesseract_binary"],
        details="synthetic unavailable dependency status",
    )

    report = run_tesseract_benchmark(dependency_status=dependency_status)

    assert report["status"] == "skipped"
    assert report["dependency_available"] is False
    assert report["fixture_count_tested"] == 0
    assert report["quality_gate_status"] == "NOT_RUN"
    assert "optional local dependencies are unavailable" in report["message"]


def test_tesseract_benchmark_does_not_make_provider_default_or_active() -> None:
    provider = TesseractLocalOcrProvider(benchmark_mode=True)
    dependency_status = ProviderDependencyStatus(
        provider_id=TESSERACT_PROVIDER_ID,
        available=False,
        python_package_available=False,
        system_binary_available=False,
        checked_dependencies=["pytesseract", "Pillow", "tesseract_binary"],
        details="synthetic unavailable dependency status",
    )

    report = run_tesseract_benchmark(
        provider=provider,
        dependency_status=dependency_status,
    )

    assert report["provider_name"] == "tesseract_local_candidate"
    assert provider.enabled_by_default is False
    assert provider.prototype_allowed is False
    assert provider.benchmark_only is True


def test_actual_tesseract_extraction_is_conditional_and_unverified() -> None:
    dependency_status = get_provider_dependency_status(TESSERACT_PROVIDER_ID)
    if not dependency_status.available:
        pytest.skip("Optional local Tesseract dependencies are not installed.")

    provider = TesseractLocalOcrProvider(benchmark_mode=True)
    case_groups = load_tesseract_benchmark_cases()
    first_case = case_groups["image_cases"][0]
    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "evaluation"
        / "ocr_fixtures"
        / first_case["fixture_filename"]
    )

    try:
        result = provider.extract_text(
            file_bytes=fixture_path.read_bytes(),
            filename=first_case["fixture_filename"],
            content_type="image/png",
        )
    except ProviderUnavailableError as error:
        pytest.skip(f"Optional local Tesseract extraction failed safely: {error}")

    assert result.provider_name == "tesseract_local_candidate"
    assert result.unverified_ocr_output is True
    assert result.pharmacist_review_required is True
    assert result.can_send_to_analysis is False


def test_tesseract_benchmark_script_runs_without_being_a_gate() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/benchmark_tesseract_ocr.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Local Tesseract OCR Benchmark" in result.stdout
    assert "not clinical validation" in result.stdout
    assert "Tesseract remains disabled by default" in result.stdout


def test_tesseract_benchmark_diagnostics_include_empty_status_and_normalized_text() -> None:
    case_groups = load_tesseract_benchmark_cases()
    case = next(
        fixture_case
        for fixture_case in case_groups["image_cases"]
        if fixture_case["fixture_filename"] == "synthetic_paracetamol_clean.png"
    )
    provider = _FakeTesseractProvider(
        "SYNTHETIC PRESCRIPTION - NOT REAL Medication Paracetamol 500 mg Pharmacist review required"
    )

    result = evaluate_tesseract_case(case=case, provider=provider)

    assert result["ocr_output_empty"] is False
    assert "paracetamol" in result["normalized_extracted_text"]
    assert result["reference_text"] == case["expected_corrected_text"]
    assert result["detected_medication_terms"] == ["paracetamol"]
    assert result["selected_preprocessing_variant"] in {
        "raw",
        "grayscale",
        "grayscale_upscale_2x",
        "contrast_upscale_2x",
        "threshold_upscale_2x",
    }
    assert result["preprocessing_attempts"]


def test_tesseract_benchmark_diagnostics_flag_empty_output() -> None:
    case_groups = load_tesseract_benchmark_cases()
    case = case_groups["image_cases"][0]
    provider = _FakeTesseractProvider("")

    result = evaluate_tesseract_case(case=case, provider=provider)

    assert result["ocr_output_empty"] is True
    assert result["normalized_extracted_text"] == ""
    assert "medication_detection_mismatch" in result["failed_checks"]


class _FakeTesseractProvider(TesseractLocalOcrProvider):
    def __init__(self, extracted_text: str) -> None:
        super().__init__(benchmark_mode=True)
        self.extracted_text = extracted_text

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OcrExtractedText:
        return OcrExtractedText(
            extracted_text=self.extracted_text,
            confidence_score=0.9 if self.extracted_text else 0.0,
            provider_name=self.provider_name,
            is_external_provider=False,
            stores_images=False,
            requires_network=False,
            supported_content_types=sorted(self.supported_content_types),
            unverified_ocr_output=True,
            pharmacist_review_required=True,
            privacy_warnings=[],
            detected_possible_identifiers=[],
            correction_required=True,
            can_send_to_analysis=False,
        )
