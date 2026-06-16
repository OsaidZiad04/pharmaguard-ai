from __future__ import annotations

from dataclasses import asdict, dataclass

from app.ocr.provider_dependencies import (
    TESSERACT_PROVIDER_ID,
    get_provider_dependency_status,
)
from app.ocr.provider_candidates import (
    OcrProviderCandidate,
    candidate_allowed_in_prototype,
)


ACTIVE_PROVIDER_IDS = {"mock_ocr_phase_2a", "synthetic_fixture_phase_2c"}
ADAPTER_DEFINED_PROVIDER_IDS = ACTIVE_PROVIDER_IDS | {TESSERACT_PROVIDER_ID}


@dataclass(frozen=True)
class ProviderSwapReadinessResult:
    provider_id: str
    ready_for_prototype: bool
    ready_for_future_evaluation: bool
    blocking_reasons: list[str]
    warnings: list[str]
    required_next_steps: list[str]

    def model_dump(self) -> dict:
        return asdict(self)


def assess_provider_swap_readiness(
    candidate: OcrProviderCandidate,
) -> ProviderSwapReadinessResult:
    blocking_reasons: list[str] = []
    warnings: list[str] = []
    required_next_steps: list[str] = []

    dependency_status = get_provider_dependency_status(candidate.provider_id)

    if candidate.provider_id not in ADAPTER_DEFINED_PROVIDER_IDS:
        blocking_reasons.append("Provider does not expose an active BaseOcrProvider adapter.")
        required_next_steps.append("Implement a provider adapter behind BaseOcrProvider.")
    elif candidate.provider_id not in ACTIVE_PROVIDER_IDS:
        blocking_reasons.append("Provider adapter exists but is disabled by default.")
        required_next_steps.append("Keep provider disabled until dependency and safety gates pass.")
    if candidate.current_status != "implemented":
        blocking_reasons.append("Provider is not implemented in the current codebase.")
    if candidate.requires_network:
        blocking_reasons.append("Networked OCR providers are blocked in prototype mode.")
        required_next_steps.append("Complete formal privacy and security review.")
    if candidate.stores_images:
        blocking_reasons.append("Image-storing OCR providers are blocked in prototype mode.")
        required_next_steps.append("Define image retention, access control, and deletion policy.")
    if candidate.requires_system_dependency:
        warnings.append("Provider requires system dependency review.")
        required_next_steps.append("Document install, patching, and deployment constraints.")
        if not dependency_status.available:
            blocking_reasons.append("Provider dependency checks are not satisfied.")
            required_next_steps.append("Install and verify optional local dependencies outside prototype mode.")
    if candidate.provider_id == TESSERACT_PROVIDER_ID:
        if dependency_status.available:
            warnings.append(
                "Local Tesseract dependencies are detected for benchmark-only evaluation."
            )
        else:
            warnings.append(
                "Local Tesseract dependencies are not available for optional benchmarking."
            )
        required_next_steps.append(
            "Run synthetic Tesseract benchmarks before any provider policy change."
        )
    if candidate.requires_model_download:
        warnings.append("Provider requires model download/cache review.")
        required_next_steps.append("Define model cache location and offline install policy.")
    if "output_unverified" not in candidate.required_quality_gates:
        blocking_reasons.append("Candidate must require unverified OCR output.")
    if "pharmacist_correction_required" not in candidate.required_quality_gates:
        blocking_reasons.append("Candidate must require pharmacist correction before analysis.")
    if "synthetic_benchmark_pass" not in candidate.required_quality_gates:
        blocking_reasons.append("Candidate must pass synthetic OCR benchmarks before use.")
    if "possible_identifier_warnings" not in candidate.required_privacy_controls:
        warnings.append("Candidate should include possible identifier warning controls.")

    ready_for_prototype = candidate_allowed_in_prototype(candidate) and not blocking_reasons
    ready_for_future_evaluation = (
        candidate.production_possible_after_review
        and not candidate.prototype_allowed
        and candidate.current_status in {"planned", "disallowed_for_prototype"}
    )

    if not ready_for_prototype and not required_next_steps:
        required_next_steps.append("Resolve blocking reasons before any provider activation.")

    return ProviderSwapReadinessResult(
        provider_id=candidate.provider_id,
        ready_for_prototype=ready_for_prototype,
        ready_for_future_evaluation=ready_for_future_evaluation,
        blocking_reasons=sorted(set(blocking_reasons)),
        warnings=sorted(set(warnings)),
        required_next_steps=sorted(set(required_next_steps)),
    )
