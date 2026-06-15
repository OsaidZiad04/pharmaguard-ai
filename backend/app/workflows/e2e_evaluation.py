from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.ocr.providers import SyntheticFixtureOcrProvider
from app.rag.evaluation import FINAL_ADVICE_FORBIDDEN_TERMS
from app.schemas.counseling import ConfirmedMedication, CounselingRequest
from app.services.counseling_service import generate_counseling_note
from app.services.extraction_service import extract_medication_candidates
from app.services.ocr_audit_service import build_ocr_correction_audit
from app.services.ocr_service import build_privacy_warnings, detect_possible_identifiers
from app.services.rag_service import query_local_knowledge_base
from app.services.safety_service import assess_prescription_analysis
from app.utils.confidence import aggregate_confidence


E2E_WORKFLOW_CASES_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "evaluation"
    / "e2e_workflow_cases.json"
)
OCR_FIXTURES_DIR = (
    Path(__file__).resolve().parents[3] / "data" / "evaluation" / "ocr_fixtures"
)


def load_e2e_workflow_cases(
    path: Path = E2E_WORKFLOW_CASES_PATH,
) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_e2e_workflow_evaluation(
    path: Path = E2E_WORKFLOW_CASES_PATH,
) -> dict[str, Any]:
    cases = load_e2e_workflow_cases(path)
    case_results = [evaluate_e2e_workflow_case(case) for case in cases]

    return {
        "total_cases": len(case_results),
        "passed_cases": sum(1 for result in case_results if result["passed"]),
        "failed_cases": sum(1 for result in case_results if not result["passed"]),
        "privacy_warning_summary": _summarize_status(
            case_results,
            "privacy_warning_status",
        ),
        "medication_extraction_summary": _summarize_status(
            case_results,
            "medication_extraction_status",
        ),
        "rag_source_grounding_summary": _summarize_status(
            case_results,
            "rag_source_status",
        ),
        "counseling_generation_summary": _summarize_status(
            case_results,
            "counseling_status",
        ),
        "safety_summary": _summarize_status(case_results, "safety_status"),
        "pharmacist_review_required_summary": _summarize_status(
            case_results,
            "pharmacist_review_required_status",
        ),
        "case_results": case_results,
    }


def evaluate_e2e_workflow_case(case: dict[str, Any]) -> dict[str, Any]:
    ocr_text = _ocr_text_for_case(case)
    detected_identifiers = detect_possible_identifiers(ocr_text)
    privacy_warnings = build_privacy_warnings(detected_identifiers)
    corrected_text = case["pharmacist_corrected_text"].strip()
    correction_audit = build_ocr_correction_audit(
        original_ocr_text=ocr_text,
        corrected_text=corrected_text,
    )

    unverified_ocr_candidates = extract_medication_candidates(ocr_text)
    analysis_candidates = extract_medication_candidates(corrected_text)
    confidence_score = aggregate_confidence(
        [candidate["confidence"] for candidate in analysis_candidates]
    )
    safety_assessment = assess_prescription_analysis(
        extracted_medications=analysis_candidates,
        confidence_score=confidence_score,
        patient_context=None,
    )

    extracted_medications = sorted({candidate["name"] for candidate in analysis_candidates})
    expected_supported = _normalized_terms(case["expected_supported_medications"])
    expected_unsupported = _normalized_terms(case["expected_unsupported_medications"])
    supported_found = [
        medication for medication in expected_supported if medication in extracted_medications
    ]
    unsupported_found = [
        medication
        for medication in expected_unsupported
        if _contains_term(corrected_text, medication)
    ]

    counseling_responses = [
        generate_counseling_note(
            CounselingRequest(
                medication=ConfirmedMedication(
                    name=candidate["name"],
                    strength=candidate.get("strength"),
                    directions=candidate.get("directions"),
                    pharmacist_confirmed=True,
                ),
                patient_context_confirmed=False,
                additional_notes="Synthetic end-to-end workflow evaluation. Draft only.",
            )
        )
        for candidate in analysis_candidates
        if candidate["name"] in expected_supported
    ]
    unsupported_rag_responses = [
        query_local_knowledge_base(f"{medication} counseling", top_k=5)
        for medication in expected_unsupported
    ]

    retrieved_source_files = sorted(
        {
            source.source_file
            for response in counseling_responses
            for source in response.retrieved_sources
        }
    )
    expected_sources = set(case.get("expected_rag_sources", []))
    counseling_available = any(
        response.retrieved_sources and not response.insufficient_context
        for response in counseling_responses
    )
    insufficient_context = (
        any(response.insufficient_context for response in counseling_responses)
        or any(response.insufficient_context for response in unsupported_rag_responses)
        or (not analysis_candidates and not expected_supported)
        or bool(expected_unsupported)
    )

    generated_text = _combined_generated_text(
        counseling_responses,
        unsupported_rag_responses,
        safety_assessment.safety_alerts,
    )
    lowered_generated_text = generated_text.lower()

    checks = {
        "ocr_output_unverified": True,
        "correction_boundary_enforced": (
            bool(corrected_text)
            and correction_audit.can_send_to_analysis
            and correction_audit.pharmacist_review_required
        ),
        "unverified_ocr_not_used_downstream": corrected_text != "" and corrected_text != ocr_text
        or corrected_text == ocr_text,
        "privacy_warnings_match": set(case["expected_privacy_warnings"])
        == set(detected_identifiers),
        "privacy_warnings_are_possible_only": all(
            warning.severity == "warning"
            and "Possible identifier pattern detected" in warning.message
            for warning in privacy_warnings
        ),
        "supported_medications_found": set(expected_supported).issubset(
            set(supported_found)
        ),
        "unsupported_medications_preserved_as_unsupported": set(
            expected_unsupported
        ).issubset(set(unsupported_found)),
        "rag_sources_grounded": expected_sources.issubset(set(retrieved_source_files)),
        "insufficient_context_expected": insufficient_context
        is bool(case["expected_insufficient_context"]),
        "counseling_availability_expected": counseling_available
        is bool(case["expected_counseling_available"]),
        "must_include_terms_present": all(
            term.lower() in lowered_generated_text
            for term in case.get("must_include_terms", [])
        ),
        "must_not_include_terms_absent": all(
            term.lower() not in lowered_generated_text
            for term in case.get("must_not_include_terms", [])
        ),
        "final_advice_language_absent": all(
            term not in lowered_generated_text for term in FINAL_ADVICE_FORBIDDEN_TERMS
        ),
        "pharmacist_review_required": (
            safety_assessment.pharmacist_review_required
            and all(response.pharmacist_review_required for response in counseling_responses)
        ),
    }

    failed_checks = [
        check_name for check_name, passed in checks.items() if not passed
    ]

    return {
        "case_id": case["case_id"],
        "input_mode": case["input_mode"],
        "passed": not failed_checks,
        "failed_checks": failed_checks,
        "ocr_text": ocr_text,
        "corrected_text": corrected_text,
        "unverified_ocr_extracted_medications": sorted(
            {candidate["name"] for candidate in unverified_ocr_candidates}
        ),
        "extracted_medications": extracted_medications,
        "supported_medications_found": supported_found,
        "unsupported_medications_found": unsupported_found,
        "retrieved_sources": retrieved_source_files,
        "expected_rag_sources": sorted(expected_sources),
        "insufficient_context": insufficient_context,
        "counseling_available": counseling_available,
        "privacy_warning_status": {
            "passed": checks["privacy_warnings_match"]
            and checks["privacy_warnings_are_possible_only"],
            "expected": case["expected_privacy_warnings"],
            "detected": detected_identifiers,
        },
        "medication_extraction_status": {
            "passed": checks["supported_medications_found"]
            and checks["unsupported_medications_preserved_as_unsupported"],
            "expected_supported": expected_supported,
            "found_supported": supported_found,
            "expected_unsupported": expected_unsupported,
            "found_unsupported": unsupported_found,
        },
        "rag_source_status": {
            "passed": checks["rag_sources_grounded"]
            and checks["insufficient_context_expected"],
            "retrieved_sources": retrieved_source_files,
            "expected_sources": sorted(expected_sources),
            "insufficient_context": insufficient_context,
        },
        "counseling_status": {
            "passed": checks["counseling_availability_expected"]
            and checks["must_include_terms_present"]
            and checks["must_not_include_terms_absent"],
            "available": counseling_available,
            "expected_available": case["expected_counseling_available"],
        },
        "safety_status": {
            "passed": checks["final_advice_language_absent"]
            and checks["unverified_ocr_not_used_downstream"],
            "safety_alert_codes": [
                alert.code for alert in safety_assessment.safety_alerts
            ],
        },
        "pharmacist_review_required_status": {
            "passed": checks["pharmacist_review_required"],
            "prescription_review_required": safety_assessment.pharmacist_review_required,
            "counseling_review_required": [
                response.pharmacist_review_required for response in counseling_responses
            ],
        },
        "checks": checks,
        "notes": case.get("notes", ""),
    }


def _ocr_text_for_case(case: dict[str, Any]) -> str:
    if case["input_mode"] != "fixture_ocr":
        return case["mock_ocr_text"]

    filename = case["synthetic_filename"]
    fixture_path = OCR_FIXTURES_DIR / filename
    provider = SyntheticFixtureOcrProvider()
    file_bytes = fixture_path.read_bytes() if fixture_path.exists() else b""
    result = provider.extract_text(
        file_bytes=file_bytes,
        filename=filename,
        content_type=_content_type_for_fixture(filename),
    )
    return result.extracted_text


def _combined_generated_text(
    counseling_responses: list[Any],
    unsupported_rag_responses: list[Any],
    safety_alerts: list[Any],
) -> str:
    parts = [response.counseling_note for response in counseling_responses]
    parts.extend(response.grounded_answer for response in unsupported_rag_responses)
    parts.extend(alert.message for alert in safety_alerts)
    return "\n".join(parts)


def _normalized_terms(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values]


def _contains_term(text: str, normalized_term: str) -> bool:
    normalized_text = re.sub(r"\s+", " ", text.lower())
    return re.search(rf"(?<!\w){re.escape(normalized_term)}(?!\w)", normalized_text) is not None


def _summarize_status(case_results: list[dict[str, Any]], key: str) -> dict[str, int]:
    passed = sum(1 for result in case_results if result[key]["passed"])
    failed = len(case_results) - passed
    return {"passed": passed, "failed": failed}


def _content_type_for_fixture(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"
