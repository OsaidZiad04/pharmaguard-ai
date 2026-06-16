from pydantic import BaseModel, Field

from app.safety.safety_models import MedicationSafetyRuleResult
from app.schemas.safety import SafetyAlert


class PatientContext(BaseModel):
    age: int | None = None
    pregnancy_status: str | None = None
    allergies: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)


class PrescriptionTextRequest(BaseModel):
    raw_text: str = Field(min_length=1)
    patient_context: PatientContext | None = None


class ExtractedMedication(BaseModel):
    name: str
    matched_text: str
    strength: str | None = None
    directions: str | None = None
    source_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    is_known: bool = True


class PrescriptionAnalysisResponse(BaseModel):
    extracted_medications: list[ExtractedMedication]
    confidence_score: float = Field(ge=0.0, le=1.0)
    missing_information: list[str]
    safety_alerts: list[SafetyAlert]
    safety_findings: list[MedicationSafetyRuleResult] = Field(default_factory=list)
    pharmacist_review_required: bool = True
