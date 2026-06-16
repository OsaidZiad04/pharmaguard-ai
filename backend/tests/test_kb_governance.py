from pathlib import Path

from app.kb.governance import (
    is_profile_allowed_for_counseling_draft,
    is_profile_allowed_for_patient_facing_output,
    load_source_catalog,
    validate_governance_metadata,
)
from app.kb.registry import DrugRegistryStore, get_drug_registry
from app.kb.schema import DrugRegistryEntry


def test_source_catalog_loads_with_local_placeholder_policy() -> None:
    catalog = load_source_catalog()
    categories = {entry.source_category: entry for entry in catalog.source_categories}

    assert "local_placeholder" in categories
    assert categories["local_placeholder"].allowed_for_clinical_use is False
    assert categories["local_placeholder"].requires_pharmacist_review is True


def test_current_profiles_have_draft_governance_metadata() -> None:
    registry = get_drug_registry()
    report = validate_governance_metadata()

    assert report.valid is True
    assert report.total_profiles == 15
    assert report.enabled_for_rag_profiles == 15
    assert report.profiles_by_source_status == {"placeholder_educational": 15}
    assert report.profiles_by_review_status == {"draft": 15}
    assert report.profiles_by_clinical_validation_status == {"not_validated": 15}
    assert report.patient_facing_allowed_count == 0
    assert report.counseling_draft_allowed_count == 15
    assert report.pharmacist_review_required_count == 15

    for entry in registry.entries:
        assert entry.profile_id == f"profile_{entry.generic_name}"
        assert entry.canonical_name == entry.generic_name
        assert entry.patient_facing_allowed is False
        assert entry.counseling_draft_allowed is True
        assert entry.requires_pharmacist_review is True
        assert entry.clinical_validation_status == "not_validated"
        assert is_profile_allowed_for_patient_facing_output(entry) is False
        assert is_profile_allowed_for_counseling_draft(entry) is True


def test_governance_blocks_patient_facing_without_review() -> None:
    store = DrugRegistryStore(
        entries=[
            _entry(
                "testdrug",
                patient_facing_allowed=True,
                review_status="draft",
                clinical_validation_status="not_validated",
            )
        ],
        profiles_dir=Path("."),
    )

    report = validate_governance_metadata(registry=store)

    assert report.valid is False
    assert any(
        issue.code == "patient_facing_without_validated_review"
        for issue in report.blocking_issues
    )


def test_governance_blocks_pharmacist_reviewed_without_reviewer_and_date() -> None:
    store = DrugRegistryStore(
        entries=[
            _entry(
                "revieweddrug",
                review_status="reviewed",
                source_status="trusted_source_ready",
                clinical_validation_status="pharmacist_reviewed",
                source_refs=["SYNTHETIC-SOURCE-001"],
            )
        ],
        profiles_dir=Path("."),
    )

    report = validate_governance_metadata(registry=store)

    assert report.valid is False
    assert any(
        issue.code == "clinical_validation_missing_review_metadata"
        for issue in report.blocking_issues
    )


def test_governance_blocks_alias_conflicts() -> None:
    store = DrugRegistryStore(
        entries=[
            _entry("drug_a", aliases=["sharedbrand"]),
            _entry("drug_b", aliases=["sharedbrand"]),
        ],
        profiles_dir=Path("."),
    )

    report = validate_governance_metadata(registry=store)

    assert report.valid is False
    assert any(issue.code == "duplicate_alias" for issue in report.blocking_issues)


def _entry(
    drug_id: str,
    aliases: list[str] | None = None,
    review_status: str = "draft",
    source_status: str = "placeholder_educational",
    clinical_validation_status: str = "not_validated",
    patient_facing_allowed: bool = False,
    source_refs: list[str] | None = None,
) -> DrugRegistryEntry:
    return DrugRegistryEntry(
        drug_id=drug_id,
        profile_id=f"profile_{drug_id}",
        generic_name=drug_id,
        canonical_name=drug_id,
        display_name=drug_id.replace("_", " ").title(),
        profile_file=f"{drug_id}.md",
        aliases=aliases or [],
        drug_class_general="test placeholder",
        common_context_tags=[],
        review_status=review_status,
        reviewed_by=None,
        last_reviewed=None,
        source_status=source_status,
        source_notes="Test fixture.",
        safety_notes=["Pharmacist review required."],
        enabled_for_rag=True,
        clinical_validation_status=clinical_validation_status,
        requires_pharmacist_review=True,
        patient_facing_allowed=patient_facing_allowed,
        counseling_draft_allowed=True,
        source_refs=source_refs or [],
        last_reviewed_at=None,
        reviewed_by_role=None,
        notes="Synthetic governance test fixture.",
    )
