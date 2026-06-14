from pydantic import BaseModel, Field

from app.schemas.safety import SafetyAlert


class DrugCard(BaseModel):
    name: str
    generic_name: str
    aliases: list[str] = Field(default_factory=list)
    category: str
    common_uses: list[str]
    pharmacist_notes: list[str]
    counseling_points: list[str]
    safety_considerations: list[str]
    source: str = "local_mock_index"
    pharmacist_review_required: bool = True


class DrugLookupResponse(BaseModel):
    found: bool
    drug: DrugCard | None = None
    safety_alerts: list[SafetyAlert] = Field(default_factory=list)
    pharmacist_review_required: bool = True
