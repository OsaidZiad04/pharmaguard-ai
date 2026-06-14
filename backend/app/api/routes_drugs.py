from fastapi import APIRouter

from app.schemas.drug import DrugLookupResponse
from app.services.drug_lookup_service import lookup_drug_card

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("/{drug_name}", response_model=DrugLookupResponse)
def get_drug(drug_name: str) -> DrugLookupResponse:
    return lookup_drug_card(drug_name)
