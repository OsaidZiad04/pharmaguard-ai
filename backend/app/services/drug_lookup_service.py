import json
from functools import lru_cache
from pathlib import Path

from app.schemas.drug import DrugCard, DrugLookupResponse
from app.schemas.rag import RagDrugCard
from app.services.safety_service import (
    build_missing_knowledge_base_context_alert,
    build_pharmacist_review_alert,
    build_unknown_medication_alert,
)
from app.services.rag_service import build_rag_drug_card

MOCK_INDEX_PATH = Path(__file__).resolve().parents[1] / "sample_data" / "mock_drug_index.json"


@lru_cache
def load_mock_drug_index() -> dict[str, dict]:
    with MOCK_INDEX_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def lookup_drug_card(drug_name: str) -> DrugLookupResponse:
    index = load_mock_drug_index()
    normalized_name = _normalize(drug_name)
    key = _resolve_drug_key(normalized_name, index)
    rag_name = key or normalized_name
    rag_card = build_rag_drug_card(rag_name)

    if not rag_card.insufficient_context and rag_card.retrieved_sources:
        return DrugLookupResponse(
            found=True,
            drug=_drug_card_from_rag(rag_card, index.get(key or normalized_name)),
            rag_drug_card=rag_card,
            retrieved_chunks=rag_card.retrieved_sources,
            grounded_answer=rag_card.grounded_answer,
            insufficient_context=False,
            safety_alerts=[build_pharmacist_review_alert()],
            pharmacist_review_required=True,
        )

    if not key:
        return DrugLookupResponse(
            found=False,
            drug=None,
            rag_drug_card=rag_card,
            retrieved_chunks=rag_card.retrieved_sources,
            grounded_answer=rag_card.grounded_answer,
            insufficient_context=True,
            safety_alerts=[
                build_unknown_medication_alert(drug_name),
                build_missing_knowledge_base_context_alert(drug_name),
                build_pharmacist_review_alert(),
            ],
            pharmacist_review_required=True,
        )

    return DrugLookupResponse(
        found=True,
        drug=DrugCard(**index[key]),
        rag_drug_card=rag_card,
        retrieved_chunks=rag_card.retrieved_sources,
        grounded_answer=rag_card.grounded_answer,
        insufficient_context=True,
        safety_alerts=[
            build_missing_knowledge_base_context_alert(drug_name),
            build_pharmacist_review_alert(),
        ],
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


def _drug_card_from_rag(
    rag_card: RagDrugCard,
    mock_profile: dict | None,
) -> DrugCard:
    fallback_name = mock_profile["name"] if mock_profile else rag_card.name.title()
    generic_name = mock_profile["generic_name"] if mock_profile else rag_card.name.lower()
    aliases = mock_profile.get("aliases", []) if mock_profile else []

    return DrugCard(
        name=fallback_name,
        generic_name=generic_name,
        aliases=aliases,
        category="Local Markdown RAG profile",
        common_uses=rag_card.overview,
        pharmacist_notes=rag_card.pharmacist_checks,
        counseling_points=rag_card.key_counseling_points,
        safety_considerations=rag_card.safety_notes,
        source=rag_card.source,
        pharmacist_review_required=True,
    )
