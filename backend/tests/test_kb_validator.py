from app.kb.registry import DRUG_PROFILES_DIR, DrugRegistryStore
from app.kb.schema import DrugRegistryEntry
from app.kb.validator import REQUIRED_PROFILE_SECTIONS, validate_drug_profiles


def test_validator_accepts_current_profiles_without_blocking_errors() -> None:
    report = validate_drug_profiles()

    assert report.valid is True
    assert report.missing_required_fields == {}
    assert report.missing_required_sections == {}
    assert report.alias_conflicts == {}
    assert report.disabled_profiles == []
    assert len(report.unreviewed_profiles) == 15
    assert all(issue.severity != "error" for issue in report.issues)


def test_all_current_profiles_include_required_sections() -> None:
    report = validate_drug_profiles()

    assert report.missing_required_sections == {}
    assert len(REQUIRED_PROFILE_SECTIONS) == 7


def test_validator_reports_duplicate_alias_conflicts() -> None:
    registry = DrugRegistryStore(
        entries=[
            _entry("paracetamol", "paracetamol.md", aliases=["sharedbrand"]),
            _entry("ibuprofen", "ibuprofen.md", aliases=["sharedbrand"]),
        ],
        profiles_dir=DRUG_PROFILES_DIR,
    )

    report = validate_drug_profiles(registry=registry)

    assert report.valid is False
    assert report.alias_conflicts == {"sharedbrand": ["ibuprofen", "paracetamol"]}
    assert any(issue.code == "duplicate_alias" for issue in report.issues)


def test_validator_represents_draft_status_clearly() -> None:
    report = validate_drug_profiles()

    assert "paracetamol" in report.unreviewed_profiles
    assert any(
        issue.code == "profile_not_pharmacist_reviewed"
        and issue.severity == "warning"
        for issue in report.issues
    )


def _entry(
    drug_id: str,
    profile_file: str,
    aliases: list[str],
) -> DrugRegistryEntry:
    return DrugRegistryEntry(
        drug_id=drug_id,
        generic_name=drug_id,
        display_name=drug_id.title(),
        profile_file=profile_file,
        aliases=aliases,
        drug_class_general="test placeholder",
        common_context_tags=[],
        review_status="draft",
        reviewed_by=None,
        last_reviewed=None,
        source_status="placeholder_educational",
        source_notes="Test fixture.",
        safety_notes=["Pharmacist review required."],
        enabled_for_rag=True,
    )
