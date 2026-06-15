from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from app.kb.schema import DrugRegistry, DrugRegistryEntry


DRUG_PROFILES_DIR = Path(__file__).resolve().parents[3] / "data" / "drug_profiles"
DEFAULT_REGISTRY_PATH = DRUG_PROFILES_DIR / "drug_registry.json"


class DrugRegistryStore:
    """Read-only local drug registry with conservative identity lookup."""

    def __init__(
        self,
        entries: list[DrugRegistryEntry],
        profiles_dir: Path = DRUG_PROFILES_DIR,
    ) -> None:
        self.entries = entries
        self.profiles_dir = profiles_dir
        self._by_generic = {
            normalize_drug_term(entry.generic_name): entry for entry in self.entries
        }
        self._by_id = {normalize_drug_term(entry.drug_id): entry for entry in self.entries}
        self._by_alias: dict[str, DrugRegistryEntry] = {}
        self.duplicate_aliases: dict[str, list[str]] = {}
        self.missing_profile_files = [
            entry.profile_file for entry in self.entries if not self.profile_exists(entry)
        ]
        self._index_aliases()

    @classmethod
    def load(
        cls,
        registry_path: Path = DEFAULT_REGISTRY_PATH,
        profiles_dir: Path = DRUG_PROFILES_DIR,
    ) -> "DrugRegistryStore":
        with registry_path.open("r", encoding="utf-8") as file:
            registry = DrugRegistry(**json.load(file))
        return cls(entries=registry.drugs, profiles_dir=profiles_dir)

    def list_enabled_drugs(self) -> list[DrugRegistryEntry]:
        return [
            entry
            for entry in self.entries
            if entry.enabled_for_rag and entry.review_status != "disabled"
        ]

    def lookup_by_generic_name(self, generic_name: str) -> DrugRegistryEntry | None:
        entry = self._by_generic.get(normalize_drug_term(generic_name))
        if not entry or not entry.enabled_for_rag or entry.review_status == "disabled":
            return None
        return entry

    def lookup_by_alias(self, alias: str) -> DrugRegistryEntry | None:
        entry = self._by_alias.get(normalize_drug_term(alias))
        if not entry or not entry.enabled_for_rag or entry.review_status == "disabled":
            return None
        return entry

    def lookup_by_id(self, drug_id: str) -> DrugRegistryEntry | None:
        entry = self._by_id.get(normalize_drug_term(drug_id))
        if not entry or not entry.enabled_for_rag or entry.review_status == "disabled":
            return None
        return entry

    def resolve_drug_name(self, value: str) -> str | None:
        """Resolve only explicit generic names or aliases, never classes or conditions."""
        entry = self.lookup_by_generic_name(value) or self.lookup_by_alias(value)
        return entry.generic_name if entry else None

    def profile_path_for(self, entry: DrugRegistryEntry) -> Path:
        return self.profiles_dir / entry.profile_file

    def profile_exists(self, entry: DrugRegistryEntry) -> bool:
        return self.profile_path_for(entry).exists()

    def _index_aliases(self) -> None:
        alias_owners: dict[str, list[DrugRegistryEntry]] = {}
        enabled_generics = {
            normalize_drug_term(entry.generic_name): entry
            for entry in self.list_enabled_drugs()
        }
        for entry in self.list_enabled_drugs():
            for alias in entry.aliases:
                normalized_alias = normalize_drug_term(alias)
                if not normalized_alias:
                    continue
                alias_owners.setdefault(normalized_alias, []).append(entry)
                generic_owner = enabled_generics.get(normalized_alias)
                if generic_owner and generic_owner.drug_id != entry.drug_id:
                    alias_owners[normalized_alias].append(generic_owner)

        for normalized_alias, owners in alias_owners.items():
            owner_ids = sorted({owner.drug_id for owner in owners})
            if len(owner_ids) > 1:
                self.duplicate_aliases[normalized_alias] = owner_ids
                continue
            self._by_alias[normalized_alias] = owners[0]


def normalize_drug_term(value: str) -> str:
    normalized = value.strip().lower().replace("-", " ")
    return re.sub(r"\s+", " ", normalized)


@lru_cache
def get_drug_registry() -> DrugRegistryStore:
    return DrugRegistryStore.load()
