from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from app.kb.registry import (
    DEFAULT_REGISTRY_PATH,
    DRUG_PROFILES_DIR,
    DrugRegistryStore,
    get_drug_registry,
)
from app.kb.schema import (
    DrugProfileValidationIssue,
    DrugRegistry,
    DrugRegistryEntry,
    KnowledgeBaseGovernanceReport,
    SourceCatalog,
)


SOURCE_CATALOG_PATH = DRUG_PROFILES_DIR / "source_catalog.json"

GOVERNANCE_REQUIRED_FIELDS = [
    "profile_id",
    "canonical_name",
    "enabled_for_rag",
    "aliases",
    "source_status",
    "review_status",
    "clinical_validation_status",
    "requires_pharmacist_review",
    "patient_facing_allowed",
    "counseling_draft_allowed",
    "source_refs",
    "last_reviewed_at",
    "reviewed_by_role",
    "notes",
]

GOVERNANCE_REVIEW_STATUSES = {
    "draft",
    "pending_review",
    "reviewed",
    "rejected",
    "pharmacist_reviewed",
    "approved_for_demo",
    "disabled",
}
GOVERNANCE_SOURCE_STATUSES = {
    "placeholder_educational",
    "trusted_source_pending",
    "trusted_source_ready",
    "pharmacist_reviewed",
    "pharmacist_supplied",
    "public_reference_pending_review",
    "validated_reference",
}
GOVERNANCE_CLINICAL_VALIDATION_STATUSES = {
    "not_validated",
    "engineering_only",
    "pharmacist_reviewed",
}
CLINICAL_SOURCE_STATUSES_REQUIRING_REFS = {
    "trusted_source_ready",
    "pharmacist_reviewed",
    "validated_reference",
}
REVIEWED_STATUSES = {"reviewed", "pharmacist_reviewed"}


def load_source_catalog(path: Path = SOURCE_CATALOG_PATH) -> SourceCatalog:
    with path.open("r", encoding="utf-8") as file:
        return SourceCatalog(**json.load(file))


def load_governed_drug_registry(
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    profiles_dir: Path = DRUG_PROFILES_DIR,
) -> DrugRegistryStore:
    with registry_path.open("r", encoding="utf-8") as file:
        registry = DrugRegistry(**json.load(file))
    return DrugRegistryStore(entries=registry.drugs, profiles_dir=profiles_dir)


def validate_governance_metadata(
    registry: DrugRegistryStore | None = None,
    source_catalog: SourceCatalog | None = None,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> KnowledgeBaseGovernanceReport:
    registry_store = registry or get_drug_registry()
    catalog = source_catalog or load_source_catalog()
    raw_entries = _load_raw_registry_entries(registry_path) if registry is None else None
    raw_by_drug_id = {
        str(raw.get("drug_id")): raw for raw in raw_entries or []
    }
    issues: list[DrugProfileValidationIssue] = []

    source_categories = {entry.source_category for entry in catalog.source_categories}
    if "local_placeholder" not in source_categories:
        issues.append(
            _issue(
                "error",
                "missing_local_placeholder_source_category",
                "Source catalog must define local_placeholder for prototype educational profiles.",
            )
        )

    for entry in registry_store.entries:
        raw_entry = raw_by_drug_id.get(entry.drug_id)
        _validate_required_governance_fields(entry, raw_entry, issues)
        _validate_status_values(entry, issues)
        _validate_review_and_output_policy(entry, issues)
        _validate_source_policy(entry, issues)
        _validate_placeholder_policy(entry, issues)

    for alias, owners in registry_store.duplicate_aliases.items():
        issues.append(
            _issue(
                "error",
                "duplicate_alias",
                f"Alias '{alias}' maps to multiple enabled drugs: {', '.join(owners)}.",
            )
        )

    blockers = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    return summarize_governance_status(
        registry=registry_store,
        source_catalog=catalog,
        blocking_issues=blockers,
        warnings=warnings,
    )


def summarize_governance_status(
    registry: DrugRegistryStore | None = None,
    source_catalog: SourceCatalog | None = None,
    blocking_issues: list[DrugProfileValidationIssue] | None = None,
    warnings: list[DrugProfileValidationIssue] | None = None,
) -> KnowledgeBaseGovernanceReport:
    registry_store = registry or get_drug_registry()
    catalog = source_catalog or load_source_catalog()
    entries = registry_store.entries
    enabled_entries = [entry for entry in entries if entry.enabled_for_rag]

    source_counts = Counter(entry.source_status for entry in entries)
    review_counts = Counter(entry.review_status for entry in entries)
    clinical_counts = Counter(entry.clinical_validation_status for entry in entries)

    return KnowledgeBaseGovernanceReport(
        valid=not blocking_issues,
        total_profiles=len(entries),
        enabled_for_rag_profiles=len(enabled_entries),
        profiles_by_source_status=dict(sorted(source_counts.items())),
        profiles_by_review_status=dict(sorted(review_counts.items())),
        profiles_by_clinical_validation_status=dict(sorted(clinical_counts.items())),
        patient_facing_allowed_count=sum(
            1 for entry in entries if entry.patient_facing_allowed
        ),
        counseling_draft_allowed_count=sum(
            1 for entry in entries if entry.counseling_draft_allowed
        ),
        pharmacist_review_required_count=sum(
            1 for entry in entries if entry.requires_pharmacist_review
        ),
        source_catalog_categories=[
            entry.source_category for entry in catalog.source_categories
        ],
        blocking_issues=blocking_issues or [],
        warnings=warnings or [],
    )


def is_profile_clinically_validated(profile: DrugRegistryEntry) -> bool:
    return (
        profile.clinical_validation_status == "pharmacist_reviewed"
        and profile.review_status in REVIEWED_STATUSES
        and bool(profile.reviewed_by_role)
        and bool(profile.last_reviewed_at)
        and bool(profile.source_refs)
    )


def is_profile_allowed_for_patient_facing_output(profile: DrugRegistryEntry) -> bool:
    return profile.patient_facing_allowed and is_profile_clinically_validated(profile)


def is_profile_allowed_for_counseling_draft(profile: DrugRegistryEntry) -> bool:
    return (
        profile.counseling_draft_allowed
        and profile.requires_pharmacist_review
        and profile.review_status not in {"disabled", "rejected"}
    )


def governance_metadata_for_entry(entry: DrugRegistryEntry) -> dict[str, Any]:
    return {
        "source_status": entry.source_status,
        "review_status": entry.review_status,
        "clinical_validation_status": entry.clinical_validation_status,
        "requires_pharmacist_review": entry.requires_pharmacist_review,
        "patient_facing_allowed": entry.patient_facing_allowed,
        "counseling_draft_allowed": entry.counseling_draft_allowed,
    }


def _validate_required_governance_fields(
    entry: DrugRegistryEntry,
    raw_entry: dict[str, Any] | None,
    issues: list[DrugProfileValidationIssue],
) -> None:
    if raw_entry is None:
        return

    missing_fields = [
        field for field in GOVERNANCE_REQUIRED_FIELDS if field not in raw_entry
    ]
    if missing_fields:
        issues.append(
            _issue(
                "error",
                "missing_governance_fields",
                f"Registry entry is missing governance fields: {', '.join(missing_fields)}.",
                entry,
            )
        )


def _validate_status_values(
    entry: DrugRegistryEntry,
    issues: list[DrugProfileValidationIssue],
) -> None:
    if entry.review_status not in GOVERNANCE_REVIEW_STATUSES:
        issues.append(
            _issue(
                "error",
                "invalid_governance_review_status",
                f"Unsupported review_status for governance: {entry.review_status}.",
                entry,
            )
        )
    if entry.source_status not in GOVERNANCE_SOURCE_STATUSES:
        issues.append(
            _issue(
                "error",
                "invalid_governance_source_status",
                f"Unsupported source_status for governance: {entry.source_status}.",
                entry,
            )
        )
    if (
        entry.clinical_validation_status
        not in GOVERNANCE_CLINICAL_VALIDATION_STATUSES
    ):
        issues.append(
            _issue(
                "error",
                "invalid_clinical_validation_status",
                "Unsupported clinical_validation_status: "
                f"{entry.clinical_validation_status}.",
                entry,
            )
        )


def _validate_review_and_output_policy(
    entry: DrugRegistryEntry,
    issues: list[DrugProfileValidationIssue],
) -> None:
    if not entry.requires_pharmacist_review:
        issues.append(
            _issue(
                "error",
                "pharmacist_review_not_required",
                "All current KB profiles must require pharmacist review.",
                entry,
            )
        )

    if entry.patient_facing_allowed and not is_profile_clinically_validated(entry):
        issues.append(
            _issue(
                "error",
                "patient_facing_without_validated_review",
                "Patient-facing output is blocked unless the profile is pharmacist-reviewed, dated, sourced, and clinically validated.",
                entry,
            )
        )

    if (
        entry.clinical_validation_status == "pharmacist_reviewed"
        and (not entry.reviewed_by_role or not entry.last_reviewed_at)
    ):
        issues.append(
            _issue(
                "error",
                "clinical_validation_missing_review_metadata",
                "Pharmacist-reviewed clinical validation requires reviewed_by_role and last_reviewed_at.",
                entry,
            )
        )

    if entry.review_status == "draft" and entry.enabled_for_rag:
        issues.append(
            _issue(
                "warning",
                "enabled_profile_is_draft",
                "Draft profile is enabled for engineering RAG only and must not be treated as clinically validated.",
                entry,
            )
        )


def _validate_source_policy(
    entry: DrugRegistryEntry,
    issues: list[DrugProfileValidationIssue],
) -> None:
    if (
        entry.source_status in CLINICAL_SOURCE_STATUSES_REQUIRING_REFS
        and not entry.source_refs
    ):
        issues.append(
            _issue(
                "error",
                "trusted_source_missing_refs",
                "Trusted or pharmacist-reviewed source status requires source_refs.",
                entry,
            )
        )


def _validate_placeholder_policy(
    entry: DrugRegistryEntry,
    issues: list[DrugProfileValidationIssue],
) -> None:
    if entry.source_status == "placeholder_educational":
        issues.append(
            _issue(
                "warning",
                "placeholder_educational_only",
                "Profile source is placeholder educational content for prototype engineering use only.",
                entry,
            )
        )
    if entry.clinical_validation_status == "not_validated":
        issues.append(
            _issue(
                "warning",
                "profile_not_clinically_validated",
                "Profile is not clinically validated and requires pharmacist review before any patient-facing use.",
                entry,
            )
        )


def _load_raw_registry_entries(registry_path: Path) -> list[dict[str, Any]]:
    with registry_path.open("r", encoding="utf-8") as file:
        return json.load(file).get("drugs", [])


def _issue(
    severity: str,
    code: str,
    message: str,
    entry: DrugRegistryEntry | None = None,
) -> DrugProfileValidationIssue:
    return DrugProfileValidationIssue(
        severity=severity,
        code=code,
        message=message,
        drug_id=entry.drug_id if entry else None,
        profile_file=entry.profile_file if entry else None,
    )
