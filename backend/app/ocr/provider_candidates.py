from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from app.ocr.provider_dependencies import (
    TESSERACT_PROVIDER_ID,
    get_provider_dependency_status,
)


ProviderType = Literal["mock", "fixture", "local_engine", "cloud_api", "planned"]
ProviderStatus = Literal["implemented", "planned", "disallowed_for_prototype"]
PrivacyRisk = Literal["low", "medium", "high"]

OCR_PROVIDER_CANDIDATES_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "evaluation"
    / "ocr_provider_candidates.json"
)


class OcrProviderCandidate(BaseModel):
    provider_id: str
    display_name: str
    provider_type: ProviderType
    current_status: ProviderStatus
    requires_network: bool
    stores_images: bool
    requires_system_dependency: bool
    requires_model_download: bool
    expected_privacy_risk: PrivacyRisk
    prototype_allowed: bool
    production_possible_after_review: bool
    notes: str
    required_quality_gates: list[str] = Field(default_factory=list)
    required_privacy_controls: list[str] = Field(default_factory=list)
    integration_blockers: list[str] = Field(default_factory=list)


@lru_cache
def load_provider_candidates(
    path: Path = OCR_PROVIDER_CANDIDATES_PATH,
) -> tuple[OcrProviderCandidate, ...]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return tuple(OcrProviderCandidate(**entry) for entry in data)


def list_provider_candidates() -> list[OcrProviderCandidate]:
    return list(load_provider_candidates())


def get_provider_candidate(provider_id: str) -> OcrProviderCandidate | None:
    normalized_id = provider_id.strip().lower()
    for candidate in load_provider_candidates():
        if candidate.provider_id == normalized_id:
            return candidate
    return None


def candidate_allowed_in_prototype(candidate: OcrProviderCandidate) -> bool:
    dependency_status = get_provider_dependency_status(candidate.provider_id)
    return (
        candidate.prototype_allowed
        and candidate.current_status == "implemented"
        and not candidate.requires_network
        and not candidate.stores_images
        and not candidate.requires_model_download
        and (not candidate.requires_system_dependency or dependency_status.available)
    )


def summarize_candidate_readiness(candidate: OcrProviderCandidate) -> dict:
    blockers = list(candidate.integration_blockers)
    if candidate.current_status != "implemented":
        blockers.append("Provider is metadata-only and is not active.")
    if candidate.requires_network:
        blockers.append("Network access is disallowed in prototype mode.")
    if candidate.stores_images:
        blockers.append("Image storage is disallowed by default.")
    if candidate.requires_model_download:
        blockers.append("Model downloads are disallowed in this phase.")
    if candidate.requires_system_dependency:
        blockers.append("System dependency review is required.")
        dependency_status = get_provider_dependency_status(candidate.provider_id)
        if not dependency_status.available:
            blockers.append("Provider dependency checks are not satisfied.")

    return {
        "provider_id": candidate.provider_id,
        "display_name": candidate.display_name,
        "current_status": candidate.current_status,
        "prototype_allowed": candidate_allowed_in_prototype(candidate),
        "production_possible_after_review": candidate.production_possible_after_review,
        "expected_privacy_risk": candidate.expected_privacy_risk,
        "requires_network": candidate.requires_network,
        "stores_images": candidate.stores_images,
        "requires_system_dependency": candidate.requires_system_dependency,
        "requires_model_download": candidate.requires_model_download,
        "dependency_status": get_provider_dependency_status(
            candidate.provider_id
        ).model_dump(),
        "readiness_summary": _readiness_summary(candidate),
        "required_quality_gates": candidate.required_quality_gates,
        "required_privacy_controls": candidate.required_privacy_controls,
        "integration_blockers": sorted(set(blockers)),
    }


def _readiness_summary(candidate: OcrProviderCandidate) -> str:
    if candidate_allowed_in_prototype(candidate):
        return "Allowed for current prototype mode."
    if candidate.provider_id == TESSERACT_PROVIDER_ID:
        return "Adapter-defined but inactive; dependency and explicit enablement checks required."
    if candidate.current_status == "planned":
        return "Planned candidate only; not active or instantiated."
    return "Disallowed for current prototype mode."
