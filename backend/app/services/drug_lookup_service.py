import json
from functools import lru_cache
from pathlib import Path

from app.schemas.drug import DrugCard, DrugLookupResponse
from app.schemas.safety import SafetyAlert
from app.services.safety_service import (
    build_pharmacist_review_alert,
    build_unknown_medication_alert,
)

MOCK_INDEX_PATH = Path(__file__).resolve().parents[1] / "sample_data" / "mock_drug_index.json"


@lru_cache
def load_mock_drug_index() -> dict[str, dict]:
    with MOCK_INDEX_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def lookup_drug_card(drug_name: str) -> DrugLookupResponse:
    index = load_mock_drug_index()
    normalized_name = _normalize(drug_name)
    key = _resolve_drug_key(normalized_name, index)

    if not key:
        return DrugLookupResponse(
            found=False,
            drug=None,
            safety_alerts=[
                build_unknown_medication_alert(drug_name),
                build_pharmacist_review_alert(),
            ],
            pharmacist_review_required=True,
        )

    return DrugLookupResponse(
        found=True,
        drug=DrugCard(**index[key]),
        safety_alerts=[build_pharmacist_review_alert()],
        pharmacist_review_required=True,
    )


def _resolve_drug_key(normalized_name: str, index: dict[str, dict]) -> str | None:
    if normalized_name in index:
        return normalized_name

    for key, profile in index.items():
        aliases = [_normalize(alias) for alias in profile.get("aliases", [])]
        if normalized_name in aliases:
            return key

    return None


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", " ")
