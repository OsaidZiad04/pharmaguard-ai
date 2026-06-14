from pydantic import BaseModel, Field


class SafetyAlert(BaseModel):
    code: str
    severity: str = Field(pattern="^(info|warning|critical)$")
    message: str
    requires_pharmacist_review: bool = True
