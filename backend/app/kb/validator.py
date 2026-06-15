from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from app.kb.registry import (
    DEFAULT_REGISTRY_PATH,
    DRUG_PROFILES_DIR,
    DrugRegistryStore,
    get_drug_registry,
    normalize_drug_term,
)
from app.kb.schema import (
    DrugProfileValidationIssue,
    DrugProfileValidationReport,
    DrugRegistryEntry,
    KnowledgeBaseCoverageReport,
)


REQUIRED_PROFILE_SECTIONS = [
    "Overview",
    "Common Uses",
    "General Counseling Points",
    "Safety Notes",
    "When to Refer to Pharmacist or Physician",
    "Patient Questions to Ask",
    "Knowledge Base Limitations",
]
REQUIRED_REGISTRY_FIELDS = [
    "drug_id",
    "generic_name",
    "display_name",
    "profile_file",
    "drug_class_general",
    "source_notes",
]
ALLOWED_REVIEW_STATUSES = {
    "draft",
    "pharmacist_reviewed",
    "approved_for_demo",
    "disabled",
}
ALLOWED_SOURCE_STATUSES = {
    "placeholder_educational",
    "pharmacist_supplied",
    "public_reference_pending_review",
    "validated_reference",
}
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$", flags=re.MULTILINE)


def validate_drug_profiles(
    registry: DrugRegistryStore | None = None,
    profiles_dir: Path = DRUG_PROFILES_DIR,
) -> DrugProfileValidationReport:
    registry_store = registry or get_drug_registry()
    issues: list[DrugProfileValidationIssue] = []
    missing_required_fields: dict[str, list[str]] = {}
    missing_required_sections: dict[str, list[str]] = {}
    disabled_profiles: list[str] = []
    unreviewed_profiles: list[str] = []

    registry_files = {
        normalize_drug_term(entry.profile_file): entry for entry in registry_store.entries
    }
    markdown_files = {
        normalize_drug_term(path.name): path
        for path in profiles_dir.glob("*.md")
        if path.name != "drug_registry.json"
    }

    for entry in registry_store.entries:
        entry_missing_fields = _missing_required_fields(entry)
        if entry_missing_fields:
            missing_required_fields[entry.drug_id] = entry_missing_fields
            issues.append(
                DrugProfileValidationIssue(
                    severity="error",
                    code="missing_required_registry_fields",
                    message=f"Registry entry is missing required fields: {', '.join(entry_missing_fields)}.",
                    drug_id=entry.drug_id,
                    profile_file=entry.profile_file,
                )
            )

        if entry.review_status not in ALLOWED_REVIEW_STATUSES:
            issues.append(
                DrugProfileValidationIssue(
                    severity="error",
                    code="invalid_review_status",
                    message=f"Unsupported review_status: {entry.review_status}.",
                    drug_id=entry.drug_id,
                    profile_file=entry.profile_file,
                )
            )

        if entry.source_status not in ALLOWED_SOURCE_STATUSES:
            issues.append(
                DrugProfileValidationIssue(
                    severity="error",
                    code="invalid_source_status",
                    message=f"Unsupported source_status: {entry.source_status}.",
                    drug_id=entry.drug_id,
                    profile_file=entry.profile_file,
                )
            )

        if entry.review_status == "disabled" or not entry.enabled_for_rag:
            disabled_profiles.append(entry.drug_id)

        if entry.review_status == "draft":
            unreviewed_profiles.append(entry.drug_id)
            issues.append(
                DrugProfileValidationIssue(
                    severity="warning",
                    code="profile_not_pharmacist_reviewed",
                    message="Profile is marked draft and must not be treated as clinically validated.",
                    drug_id=entry.drug_id,
                    profile_file=entry.profile_file,
                )
            )

        profile_path = registry_store.profile_path_for(entry)
        if not profile_path.exists():
            issues.append(
                DrugProfileValidationIssue(
                    severity="error",
                    code="profile_file_missing",
                    message="Registry entry points to a Markdown profile that does not exist.",
                    drug_id=entry.drug_id,
                    profile_file=entry.profile_file,
                )
            )
            continue

        if entry.enabled_for_rag and entry.review_status != "disabled":
            missing_sections = _missing_sections(profile_path)
            if missing_sections:
                missing_required_sections[entry.profile_file] = missing_sections
                issues.append(
                    DrugProfileValidationIssue(
                        severity="error",
                        code="missing_required_sections",
                        message=f"Markdown profile is missing sections: {', '.join(missing_sections)}.",
                        drug_id=entry.drug_id,
                        profile_file=entry.profile_file,
                    )
                )

    for markdown_name, markdown_path in markdown_files.items():
        if markdown_name not in registry_files:
            issues.append(
                DrugProfileValidationIssue(
                    severity="error",
                    code="profile_missing_registry_entry",
                    message="Markdown profile does not have a drug_registry.json entry.",
                    profile_file=markdown_path.name,
                )
            )

    alias_conflicts = registry_store.duplicate_aliases
    for alias, owners in alias_conflicts.items():
        issues.append(
            DrugProfileValidationIssue(
                severity="error",
                code="duplicate_alias",
                message=f"Alias '{alias}' maps to multiple enabled drugs: {', '.join(owners)}.",
            )
        )

    valid = not any(issue.severity == "error" for issue in issues)
    return DrugProfileValidationReport(
        valid=valid,
        issues=issues,
        missing_required_fields=missing_required_fields,
        missing_required_sections=missing_required_sections,
        alias_conflicts=alias_conflicts,
        disabled_profiles=sorted(disabled_profiles),
        unreviewed_profiles=sorted(unreviewed_profiles),
    )


def build_coverage_report(
    registry: DrugRegistryStore | None = None,
    profiles_dir: Path = DRUG_PROFILES_DIR,
) -> KnowledgeBaseCoverageReport:
    registry_store = registry or get_drug_registry()
    enabled_entries = registry_store.list_enabled_drugs()
    validation_report = validate_drug_profiles(
        registry=registry_store,
        profiles_dir=profiles_dir,
    )
    review_counts = Counter(entry.review_status for entry in registry_store.entries)
    source_counts = Counter(entry.source_status for entry in registry_store.entries)

    return KnowledgeBaseCoverageReport(
        total_profiles=len(registry_store.entries),
        total_enabled_profiles=len(enabled_entries),
        total_aliases=sum(len(entry.aliases) for entry in enabled_entries),
        profiles_by_review_status=dict(sorted(review_counts.items())),
        profiles_by_source_status=dict(sorted(source_counts.items())),
        validation_report=validation_report,
    )


def _missing_required_fields(entry: DrugRegistryEntry) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_REGISTRY_FIELDS:
        value = getattr(entry, field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


def _missing_sections(profile_path: Path) -> list[str]:
    text = profile_path.read_text(encoding="utf-8")
    headings = {heading.strip() for heading in HEADING_PATTERN.findall(text)}
    return [section for section in REQUIRED_PROFILE_SECTIONS if section not in headings]

