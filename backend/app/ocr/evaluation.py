from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean
from typing import Any

from app.ocr.providers import MockOcrProvider, SyntheticFixtureOcrProvider
from app.ocr.quality_gates import evaluate_quality_gates_for_provider_summaries
from app.schemas.ocr import OcrEvaluationResult
from app.services.extraction_service import extract_medication_candidates
from app.services.ocr_service import detect_possible_identifiers, list_available_ocr_providers


OCR_EVAL_CASES_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "evaluation" / "ocr_eval_cases.json"
)
OCR_FIXTURES_DIR = Path(__file__).resolve().parents[3] / "data" / "evaluation" / "ocr_fixtures"


def character_error_rate(reference: str, prediction: str) -> float:
    reference_chars = list(reference or "")
    prediction_chars = list(prediction or "")
    return _normalized_edit_distance(reference_chars, prediction_chars)


def word_error_rate(reference: str, prediction: str) -> float:
    return _normalized_edit_distance(_tokens(reference), _tokens(prediction))


def token_overlap_score(reference: str, prediction: str) -> float:
    reference_tokens = set(_tokens(reference))
    prediction_tokens = set(_tokens(prediction))
    if not reference_tokens and not prediction_tokens:
        return 1.0
    if not reference_tokens or not prediction_tokens:
        return 0.0
    return round(len(reference_tokens & prediction_tokens) / len(reference_tokens | prediction_tokens), 4)


def medication_detection_hit(
    expected_medications: list[str],
    extracted_or_corrected_text: str,
) -> bool:
    normalized_text = _normalize_text(extracted_or_corrected_text)
    expected = [_normalize_text(medication) for medication in expected_medications]
    if not expected:
        return len(_supported_detected_medication_terms(extracted_or_corrected_text)) == 0
    return all(_contains_term(normalized_text, medication) for medication in expected)


def privacy_warning_match(
    expected_identifiers: list[str],
    detected_identifiers: list[str],
) -> bool:
    return set(expected_identifiers) == set(detected_identifiers)


def load_ocr_eval_cases(path: Path = OCR_EVAL_CASES_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_ocr_evaluation(path: Path = OCR_EVAL_CASES_PATH) -> dict[str, Any]:
    from app.services.ocr_audit_service import build_ocr_correction_audit

    cases = load_ocr_eval_cases(path)
    results: list[OcrEvaluationResult] = []

    for case in cases:
        fixture_backed = bool(case.get("fixture_filename"))
        provider_name = (
            SyntheticFixtureOcrProvider.provider_name
            if fixture_backed
            else MockOcrProvider.provider_name
        )
        mock_text = _ocr_text_for_case(case)
        corrected_text = case["expected_corrected_text"]
        detected_identifiers = detect_possible_identifiers(mock_text)
        expected_identifiers = case["expected_possible_identifiers"]
        warning_count_match = (
            len(detected_identifiers) == case["expected_privacy_warning_count"]
        )
        medication_hit = medication_detection_hit(
            case["expected_medications"],
            corrected_text,
        )
        privacy_match = privacy_warning_match(expected_identifiers, detected_identifiers)
        audit = build_ocr_correction_audit(
            original_ocr_text=mock_text,
            corrected_text=corrected_text,
        )
        cer = character_error_rate(corrected_text, mock_text)
        wer = word_error_rate(corrected_text, mock_text)
        overlap = token_overlap_score(corrected_text, mock_text)
        passed = (
            medication_hit
            and privacy_match
            and warning_count_match
            and audit.pharmacist_review_required
            and audit.can_send_to_analysis
        )

        results.append(
            OcrEvaluationResult(
                case_id=case["case_id"],
                provider_name=provider_name,
                fixture_backed=fixture_backed,
                passed=passed,
                character_error_rate=cer,
                word_error_rate=wer,
                token_overlap_score=overlap,
                medication_detection_hit=medication_hit,
                privacy_warning_match=privacy_match,
                output_unverified=True,
                detected_possible_identifiers=detected_identifiers,
                expected_possible_identifiers=expected_identifiers,
                notes=case.get("notes"),
            )
        )

    total_cases = len(results)
    passed_cases = sum(1 for result in results if result.passed)
    failed_cases = total_cases - passed_cases
    fixture_backed_cases = sum(1 for case in cases if case.get("fixture_filename"))
    text_only_cases = total_cases - fixture_backed_cases
    provider_summaries = _provider_summaries(results)
    quality_gate_results = evaluate_quality_gates_for_provider_summaries(
        providers=list_available_ocr_providers(),
        provider_summaries=provider_summaries,
    )
    quality_gate_summary = {
        "passed": sum(1 for result in quality_gate_results if result.passed),
        "failed": sum(1 for result in quality_gate_results if not result.passed),
        "results": [result.model_dump() for result in quality_gate_results],
    }

    return {
        "total_cases": total_cases,
        "text_only_cases": text_only_cases,
        "fixture_backed_cases": fixture_backed_cases,
        "provider_used": "mock_ocr_phase_2a + synthetic_fixture_phase_2c",
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "average_character_error_rate": _mean(
            [result.character_error_rate for result in results]
        ),
        "average_word_error_rate": _mean([result.word_error_rate for result in results]),
        "medication_detection_summary": {
            "passed": sum(1 for result in results if result.medication_detection_hit),
            "failed": sum(1 for result in results if not result.medication_detection_hit),
        },
        "privacy_warning_summary": {
            "passed": sum(1 for result in results if result.privacy_warning_match),
            "failed": sum(1 for result in results if not result.privacy_warning_match),
        },
        "provider_summaries": provider_summaries,
        "quality_gate_summary": quality_gate_summary,
        "case_results": [result.model_dump() for result in results],
    }


def _ocr_text_for_case(case: dict[str, Any]) -> str:
    fixture_filename = case.get("fixture_filename")
    if not fixture_filename:
        return case["mock_ocr_text"]

    fixture_path = OCR_FIXTURES_DIR / fixture_filename
    provider = SyntheticFixtureOcrProvider()
    file_bytes = fixture_path.read_bytes() if fixture_path.exists() else b""
    result = provider.extract_text(
        file_bytes=file_bytes,
        filename=fixture_filename,
        content_type=_content_type_for_fixture(fixture_filename),
    )
    return result.extracted_text


def _normalized_edit_distance(reference_tokens: list[str], prediction_tokens: list[str]) -> float:
    if not reference_tokens and not prediction_tokens:
        return 0.0
    if not reference_tokens:
        return 1.0
    distance = _levenshtein_distance(reference_tokens, prediction_tokens)
    return round(distance / len(reference_tokens), 4)


def _levenshtein_distance(reference_tokens: list[str], prediction_tokens: list[str]) -> int:
    previous_row = list(range(len(prediction_tokens) + 1))
    for reference_index, reference_token in enumerate(reference_tokens, start=1):
        current_row = [reference_index]
        for prediction_index, prediction_token in enumerate(prediction_tokens, start=1):
            insertion = current_row[prediction_index - 1] + 1
            deletion = previous_row[prediction_index] + 1
            substitution = previous_row[prediction_index - 1] + (
                reference_token != prediction_token
            )
            current_row.append(min(insertion, deletion, substitution))
        previous_row = current_row
    return previous_row[-1]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower().replace("-", " "))


def _contains_term(normalized_text: str, normalized_term: str) -> bool:
    if not normalized_term:
        return False
    return re.search(rf"(?<!\w){re.escape(normalized_term)}(?!\w)", normalized_text) is not None


def _supported_detected_medication_terms(text: str) -> list[str]:
    return [candidate["name"] for candidate in extract_medication_candidates(text)]


def _mean(values: list[float]) -> float:
    return round(mean(values), 4) if values else 0.0


def _provider_summaries(results: list[OcrEvaluationResult]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for provider_name in sorted({result.provider_name for result in results}):
        provider_results = [
            result for result in results if result.provider_name == provider_name
        ]
        quality_metric_results = [
            result for result in provider_results if not result.expected_possible_identifiers
        ] or provider_results
        summaries[provider_name] = {
            "provider_name": provider_name,
            "total_cases": len(provider_results),
            "passed_cases": sum(1 for result in provider_results if result.passed),
            "failed_cases": sum(1 for result in provider_results if not result.passed),
            "fixture_backed_cases": sum(1 for result in provider_results if result.fixture_backed),
            "text_only_cases": sum(1 for result in provider_results if not result.fixture_backed),
            "quality_metric_cases": len(quality_metric_results),
            "average_character_error_rate": _mean(
                [result.character_error_rate for result in quality_metric_results]
            ),
            "average_word_error_rate": _mean(
                [result.word_error_rate for result in quality_metric_results]
            ),
            "average_token_overlap_score": _mean(
                [result.token_overlap_score for result in quality_metric_results]
            ),
            "all_case_average_character_error_rate": _mean(
                [result.character_error_rate for result in provider_results]
            ),
            "all_case_average_word_error_rate": _mean(
                [result.word_error_rate for result in provider_results]
            ),
            "medication_detection_failed": sum(
                1 for result in provider_results if not result.medication_detection_hit
            ),
            "privacy_warning_failed": sum(
                1 for result in provider_results if not result.privacy_warning_match
            ),
            "output_unverified_all": all(result.output_unverified for result in provider_results),
        }
    return summaries


def _content_type_for_fixture(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"
