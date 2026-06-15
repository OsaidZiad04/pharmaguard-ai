from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

from app.kb.registry import normalize_drug_term


def import_profile_from_structured_source(source_payload: dict[str, Any]) -> dict[str, Any]:
    """Create a draft ingestion record without calling external services.

    TODO: In a later governed ingestion workflow, accept only trusted sources,
    preserve provenance/version metadata, and route every imported profile to
    pharmacist review before enabling it for RAG.
    """
    identity = normalize_drug_identity(
        source_payload.get("generic_name", ""),
        source_payload.get("aliases", []),
    )
    draft = create_draft_profile(
        generic_name=identity["generic_name"],
        display_name=source_payload.get("display_name") or identity["display_name"],
        aliases=identity["aliases"],
        source_notes="Draft imported record pending source and pharmacist review.",
    )
    draft["source_payload_keys"] = sorted(source_payload.keys())
    return require_pharmacist_review(draft)


def normalize_drug_identity(
    generic_name: str,
    aliases: list[str] | None = None,
) -> dict[str, Any]:
    """Normalize explicit names and aliases only; never infer from conditions/classes."""
    normalized_generic = normalize_drug_term(generic_name)
    normalized_aliases = sorted(
        {
            normalize_drug_term(alias)
            for alias in aliases or []
            if normalize_drug_term(alias) and normalize_drug_term(alias) != normalized_generic
        }
    )
    return {
        "generic_name": normalized_generic,
        "display_name": normalized_generic.title() if normalized_generic else "",
        "aliases": normalized_aliases,
    }


def create_draft_profile(
    generic_name: str,
    display_name: str,
    aliases: list[str] | None = None,
    source_notes: str = "Draft profile pending provenance and pharmacist review.",
) -> dict[str, Any]:
    """Return registry-shaped draft metadata for future ingestion pipelines."""
    normalized_generic = normalize_drug_term(generic_name)
    return {
        "drug_id": normalized_generic.replace(" ", "_"),
        "generic_name": normalized_generic,
        "display_name": display_name,
        "profile_file": f"{normalized_generic.replace(' ', '_')}.md",
        "aliases": aliases or [],
        "drug_class_general": "pending review",
        "common_context_tags": [],
        "review_status": "draft",
        "reviewed_by": None,
        "last_reviewed": None,
        "source_status": "public_reference_pending_review",
        "source_notes": source_notes,
        "safety_notes": [
            "Pharmacist review required before use.",
            "Draft ingestion placeholder only.",
        ],
        "enabled_for_rag": False,
    }


def require_pharmacist_review(profile: dict[str, Any]) -> dict[str, Any]:
    """Mark a draft as blocked from RAG until pharmacist review occurs."""
    reviewed_profile = deepcopy(profile)
    reviewed_profile["review_status"] = "draft"
    reviewed_profile["enabled_for_rag"] = False
    reviewed_profile["requires_pharmacist_review"] = True
    return reviewed_profile


def promote_profile_to_approved(
    profile: dict[str, Any],
    reviewer: str,
    approval_date: date | None = None,
) -> dict[str, Any]:
    """Prepare a demo-approved registry record after human pharmacist review."""
    approved_profile = deepcopy(profile)
    approved_profile["review_status"] = "approved_for_demo"
    approved_profile["reviewed_by"] = reviewer
    approved_profile["last_reviewed"] = (approval_date or date.today()).isoformat()
    approved_profile["enabled_for_rag"] = True
    approved_profile["requires_pharmacist_review"] = True
    return approved_profile


def reject_profile(profile: dict[str, Any], reason: str) -> dict[str, Any]:
    """Disable a draft profile and retain a review note for auditability."""
    rejected_profile = deepcopy(profile)
    rejected_profile["review_status"] = "disabled"
    rejected_profile["enabled_for_rag"] = False
    rejected_profile["rejection_reason"] = reason
    rejected_profile["requires_pharmacist_review"] = True
    return rejected_profile

