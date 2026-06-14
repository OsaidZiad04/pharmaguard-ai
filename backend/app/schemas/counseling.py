from pydantic import BaseModel, Field

from app.schemas.safety import SafetyAlert


class ConfirmedMedication(BaseModel):
    name: str
    strength: str | None = None
    directions: str | None = None
    pharmacist_confirmed: bool = False


class CounselingRequest(BaseModel):
    medication: ConfirmedMedication
    patient_context_confirmed: bool = False
    additional_notes: str | None = Field(default=None, max_length=500)


class CounselingResponse(BaseModel):
    counseling_note: str
    safety_alerts: list[SafetyAlert]
    pharmacist_review_required: bool = True
