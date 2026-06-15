from pathlib import Path

from app.kb.registry import DRUG_PROFILES_DIR, DrugRegistryStore, get_drug_registry
from app.kb.schema import DrugRegistryEntry


def test_registry_loads_all_current_profiles() -> None:
    registry = get_drug_registry()
    profile_files = {entry.profile_file for entry in registry.entries}
    markdown_files = {path.name for path in DRUG_PROFILES_DIR.glob("*.md")}

    assert len(registry.entries) == 15
    assert markdown_files == profile_files
    assert registry.missing_profile_files == []
    assert len(registry.list_enabled_drugs()) == 15


def test_registry_supports_generic_and_alias_lookup() -> None:
    registry = get_drug_registry()

    assert registry.lookup_by_generic_name("paracetamol").generic_name == "paracetamol"
    assert registry.lookup_by_alias("acetaminophen").generic_name == "paracetamol"
    assert registry.lookup_by_alias("Ventolin").generic_name == "salbutamol"
    assert registry.lookup_by_alias("glucophage").generic_name == "metformin"
    assert registry.lookup_by_alias("unknownbrand") is None


def test_registry_does_not_resolve_conditions_or_broad_classes() -> None:
    registry = get_drug_registry()

    for term in [
        "antihistamine",
        "antibiotic",
        "painkiller",
        "allergic rhinitis",
        "diabetes",
        "high blood pressure",
    ]:
        assert registry.resolve_drug_name(term) is None


def test_registry_detects_duplicate_aliases() -> None:
    store = DrugRegistryStore(
        entries=[
            _registry_entry("drug_a", "drug-a.md", aliases=["sharedbrand"]),
            _registry_entry("drug_b", "drug-b.md", aliases=["sharedbrand"]),
        ],
        profiles_dir=Path("."),
    )

    assert store.duplicate_aliases == {"sharedbrand": ["drug_a", "drug_b"]}
    assert store.lookup_by_alias("sharedbrand") is None


def _registry_entry(
    drug_id: str,
    profile_file: str,
    aliases: list[str] | None = None,
) -> DrugRegistryEntry:
    return DrugRegistryEntry(
        drug_id=drug_id,
        generic_name=drug_id,
        display_name=drug_id.replace("_", " ").title(),
        profile_file=profile_file,
        aliases=aliases or [],
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
