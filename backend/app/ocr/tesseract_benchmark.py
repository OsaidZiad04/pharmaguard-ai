from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Any

from app.ocr.evaluation import (
    OCR_EVAL_CASES_PATH,
    OCR_FIXTURES_DIR,
    character_error_rate,
    load_ocr_eval_cases,
    medication_detection_hit,
    privacy_warning_match,
    token_overlap_score,
    word_error_rate,
)
from app.ocr.local_tesseract_provider import (
    ProviderUnavailableError,
    TesseractLocalOcrProvider,
)
from app.ocr.provider_dependencies import (
    TESSERACT_PROVIDER_ID,
    ProviderDependencyStatus,
    get_provider_dependency_status,
)
from app.ocr.quality_gates import evaluate_provider_quality_gates
from app.services.ocr_service import detect_possible_identifiers


IMAGE_FIXTURE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def load_tesseract_benchmark_cases(
    path: Path = OCR_EVAL_CASES_PATH,
) -> dict[str, Any]:
    """Load fixture-backed cases and separate image fixtures from descriptors."""
    fixture_cases = [case for case in load_ocr_eval_cases(path) if case.get("fixture_filename")]
    image_cases: list[dict[str, Any]] = []
    skipped_descriptor_cases: list[dict[str, str]] = []
    missing_fixture_cases: list[dict[str, str]] = []

    for case in fixture_cases:
        fixture_filename = case["fixture_filename"]
        fixture_path = OCR_FIXTURES_DIR / fixture_filename
        suffix = fixture_path.suffix.lower()
        if suffix not in IMAGE_FIXTURE_SUFFIXES:
            skipped_descriptor_cases.append(
                _skipped_case(case, "descriptor_fixture_not_used_for_tesseract")
            )
            continue
        if not fixture_path.exists():
            missing_fixture_cases.append(_skipped_case(case, "fixture_file_missing"))
            continue
        image_cases.append(case)

    return {
        "fixture_cases": fixture_cases,
        "image_cases": image_cases,
        "skipped_descriptor_cases": skipped_descriptor_cases,
        "missing_fixture_cases": missing_fixture_cases,
    }


def run_tesseract_benchmark(
    path: Path = OCR_EVAL_CASES_PATH,
    provider: TesseractLocalOcrProvider | None = None,
    dependency_status: ProviderDependencyStatus | None = None,
) -> dict[str, Any]:
    """Run optional local Tesseract against approved synthetic image fixtures."""
    case_groups = load_tesseract_benchmark_cases(path)
    dependency_status = dependency_status or get_provider_dependency_status(
        TESSERACT_PROVIDER_ID
    )
    provider = provider or TesseractLocalOcrProvider(benchmark_mode=True)
    skipped_cases = (
        case_groups["skipped_descriptor_cases"] + case_groups["missing_fixture_cases"]
    )

    if not dependency_status.available:
        return _skipped_benchmark_report(
            case_groups=case_groups,
            dependency_status=dependency_status,
            message=(
                "Tesseract benchmark skipped because optional local dependencies "
                f"are unavailable. {dependency_status.details}"
            ),
        )

    case_results = [
        evaluate_tesseract_case(case=case, provider=provider)
        for case in case_groups["image_cases"]
    ]
    return summarize_tesseract_benchmark(
        case_results=case_results,
        skipped_cases=skipped_cases,
        dependency_status=dependency_status,
        provider=provider,
    )


def evaluate_tesseract_case(
    case: dict[str, Any],
    provider: TesseractLocalOcrProvider | None = None,
) -> dict[str, Any]:
    provider = provider or TesseractLocalOcrProvider(benchmark_mode=True)
    fixture_filename = case["fixture_filename"]
    fixture_path = OCR_FIXTURES_DIR / fixture_filename
    reference_text = case["expected_corrected_text"]

    extracted_text = ""
    provider_name = provider.provider_name
    output_unverified = False
    pharmacist_review_required = False
    can_send_to_analysis = False
    failed_checks: list[str] = []
    error_message: str | None = None

    try:
        result = provider.extract_text(
            file_bytes=fixture_path.read_bytes(),
            filename=fixture_filename,
            content_type=_content_type_for_fixture(fixture_filename),
        )
        extracted_text = result.extracted_text
        provider_name = result.provider_name
        output_unverified = result.unverified_ocr_output
        pharmacist_review_required = result.pharmacist_review_required
        can_send_to_analysis = result.can_send_to_analysis
    except ProviderUnavailableError as error:
        failed_checks.append("tesseract_extraction_failed")
        error_message = str(error)

    detected_identifiers = detect_possible_identifiers(extracted_text)
    expected_identifiers = case.get("expected_possible_identifiers", [])
    medication_hit = medication_detection_hit(
        case.get("expected_medications", []),
        extracted_text,
    )
    privacy_match = privacy_warning_match(expected_identifiers, detected_identifiers)
    cer = character_error_rate(reference_text, extracted_text)
    wer = word_error_rate(reference_text, extracted_text)
    overlap = token_overlap_score(reference_text, extracted_text)

    if not medication_hit:
        failed_checks.append("medication_detection_mismatch")
    if not privacy_match:
        failed_checks.append("privacy_warning_mismatch")
    if not output_unverified:
        failed_checks.append("ocr_output_not_marked_unverified")
    if not pharmacist_review_required:
        failed_checks.append("pharmacist_review_not_required")
    if can_send_to_analysis:
        failed_checks.append("unverified_ocr_marked_sendable_to_analysis")

    return {
        "case_id": case["case_id"],
        "fixture_filename": fixture_filename,
        "provider_name": provider_name,
        "passed": not failed_checks,
        "failed_checks": sorted(set(failed_checks)),
        "error_message": error_message,
        "reference_text": reference_text,
        "extracted_text": extracted_text,
        "character_error_rate": cer,
        "word_error_rate": wer,
        "token_overlap_score": overlap,
        "medication_detection_hit": medication_hit,
        "privacy_warning_match": privacy_match,
        "output_unverified": output_unverified,
        "pharmacist_review_required": pharmacist_review_required,
        "can_send_to_analysis": can_send_to_analysis,
        "detected_possible_identifiers": detected_identifiers,
        "expected_possible_identifiers": expected_identifiers,
        "notes": case.get("notes"),
    }


def summarize_tesseract_benchmark(
    case_results: list[dict[str, Any]],
    skipped_cases: list[dict[str, str]],
    dependency_status: ProviderDependencyStatus,
    provider: TesseractLocalOcrProvider | None = None,
) -> dict[str, Any]:
    provider = provider or TesseractLocalOcrProvider(benchmark_mode=True)
    metrics_summary = _metrics_summary(case_results, provider.provider_name)
    quality_gate_result = (
        evaluate_provider_quality_gates(provider, metrics_summary)
        if case_results
        else None
    )
    quality_gate_status = (
        "PASS"
        if quality_gate_result and quality_gate_result.passed
        else "FAIL"
        if quality_gate_result
        else "NOT_RUN"
    )

    return {
        "provider_name": provider.provider_name,
        "status": "completed",
        "dependency_available": dependency_status.available,
        "dependency_details": dependency_status.details,
        "fixture_count_tested": len(case_results),
        "skipped_descriptor_only_fixtures": sum(
            1
            for case in skipped_cases
            if case["reason"] == "descriptor_fixture_not_used_for_tesseract"
        ),
        "skipped_missing_fixtures": sum(
            1 for case in skipped_cases if case["reason"] == "fixture_file_missing"
        ),
        "passed_cases": sum(1 for result in case_results if result["passed"]),
        "failed_cases": sum(1 for result in case_results if not result["passed"]),
        "average_character_error_rate": metrics_summary["average_character_error_rate"],
        "average_word_error_rate": metrics_summary["average_word_error_rate"],
        "average_token_overlap_score": metrics_summary["average_token_overlap_score"],
        "medication_detection_summary": {
            "passed": sum(
                1 for result in case_results if result["medication_detection_hit"]
            ),
            "failed": metrics_summary["medication_detection_failed"],
        },
        "privacy_warning_summary": {
            "passed": sum(1 for result in case_results if result["privacy_warning_match"]),
            "failed": metrics_summary["privacy_warning_failed"],
        },
        "quality_gate_status": quality_gate_status,
        "quality_gate_result": (
            quality_gate_result.model_dump() if quality_gate_result else None
        ),
        "metrics_summary": metrics_summary,
        "case_results": case_results,
        "skipped_cases": skipped_cases,
        "note": "Synthetic engineering benchmark only; not clinical validation.",
    }


def _metrics_summary(
    case_results: list[dict[str, Any]],
    provider_name: str,
) -> dict[str, Any]:
    return {
        "provider_name": provider_name,
        "total_cases": len(case_results),
        "passed_cases": sum(1 for result in case_results if result["passed"]),
        "failed_cases": sum(1 for result in case_results if not result["passed"]),
        "fixture_backed_cases": len(case_results),
        "text_only_cases": 0,
        "average_character_error_rate": _mean(
            [result["character_error_rate"] for result in case_results]
        ),
        "average_word_error_rate": _mean(
            [result["word_error_rate"] for result in case_results]
        ),
        "average_token_overlap_score": _mean(
            [result["token_overlap_score"] for result in case_results]
        ),
        "medication_detection_failed": sum(
            1 for result in case_results if not result["medication_detection_hit"]
        ),
        "privacy_warning_failed": sum(
            1 for result in case_results if not result["privacy_warning_match"]
        ),
        "output_unverified_all": all(
            result["output_unverified"] for result in case_results
        ),
    }


def _skipped_benchmark_report(
    case_groups: dict[str, Any],
    dependency_status: ProviderDependencyStatus,
    message: str,
) -> dict[str, Any]:
    skipped_cases = (
        case_groups["skipped_descriptor_cases"] + case_groups["missing_fixture_cases"]
    )
    return {
        "provider_name": TESSERACT_PROVIDER_ID,
        "status": "skipped",
        "dependency_available": False,
        "dependency_details": dependency_status.details,
        "message": message,
        "fixture_count_tested": 0,
        "skipped_descriptor_only_fixtures": len(case_groups["skipped_descriptor_cases"]),
        "skipped_missing_fixtures": len(case_groups["missing_fixture_cases"]),
        "passed_cases": 0,
        "failed_cases": 0,
        "average_character_error_rate": 0.0,
        "average_word_error_rate": 0.0,
        "average_token_overlap_score": 0.0,
        "medication_detection_summary": {"passed": 0, "failed": 0},
        "privacy_warning_summary": {"passed": 0, "failed": 0},
        "quality_gate_status": "NOT_RUN",
        "quality_gate_result": None,
        "metrics_summary": _metrics_summary([], TESSERACT_PROVIDER_ID),
        "case_results": [],
        "skipped_cases": skipped_cases,
        "note": "Synthetic engineering benchmark only; not clinical validation.",
    }


def _skipped_case(case: dict[str, Any], reason: str) -> dict[str, str]:
    return {
        "case_id": case["case_id"],
        "fixture_filename": case["fixture_filename"],
        "reason": reason,
    }


def _content_type_for_fixture(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"


def _mean(values: list[float]) -> float:
    return round(mean(values), 4) if values else 0.0
