from pydantic import BaseModel, Field


class MedicationSafetyRuleResult(BaseModel):
    rule_id: str
    severity: str = Field(pattern="^(info|caution|warning|blocker)$")
    message: str
    detected_terms: list[str] = Field(default_factory=list)
    pharmacist_action: str
    evidence_source: str = Field(
        pattern="^(prescription_text|retrieval_metadata|kb_governance|system_policy)$"
    )
    patient_facing_allowed: bool = False


class MedicationSafetyAnalysis(BaseModel):
    findings: list[MedicationSafetyRuleResult] = Field(default_factory=list)
    pharmacist_review_required: bool = True
    patient_facing_allowed: bool = False
    interaction_check_available: bool = False
    contraindication_check_available: bool = False
    requires_trusted_source_ingestion: bool = True
