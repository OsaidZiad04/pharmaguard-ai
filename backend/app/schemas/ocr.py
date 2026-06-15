from pydantic import BaseModel, Field


class PrivacyWarning(BaseModel):
    code: str
    severity: str = Field(default="warning", pattern="^(info|warning|critical)$")
    message: str


class OcrExtractedText(BaseModel):
    extracted_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    provider_name: str
    unverified_ocr_output: bool = True
    pharmacist_review_required: bool = True
    privacy_warnings: list[PrivacyWarning] = Field(default_factory=list)
    detected_possible_identifiers: list[str] = Field(default_factory=list)
    correction_required: bool = True
    can_send_to_analysis: bool = False


class OcrImageUploadResponse(OcrExtractedText):
    filename: str
    content_type: str


class OcrCorrectionRequest(BaseModel):
    extracted_text: str = ""
    corrected_text: str = Field(min_length=1)


class OcrCorrectionResponse(BaseModel):
    corrected_text: str
    pharmacist_review_required: bool = True
    correction_required: bool = False
    can_send_to_analysis: bool = True
    privacy_warnings: list[PrivacyWarning] = Field(default_factory=list)
    detected_possible_identifiers: list[str] = Field(default_factory=list)
