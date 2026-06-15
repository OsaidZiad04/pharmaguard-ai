from pydantic import BaseModel, Field


class PrivacyWarning(BaseModel):
    code: str
    severity: str = Field(default="warning", pattern="^(info|warning|critical)$")
    message: str


class OcrExtractedText(BaseModel):
    extracted_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    provider_name: str
    is_external_provider: bool = False
    stores_images: bool = False
    requires_network: bool = False
    supported_content_types: list[str] = Field(default_factory=list)
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


class OcrCorrectionDiff(BaseModel):
    changed: bool
    character_error_rate: float = Field(ge=0.0)
    word_error_rate: float = Field(ge=0.0)
    token_overlap_score: float = Field(ge=0.0, le=1.0)


class OcrCorrectionAudit(BaseModel):
    original_ocr_text: str
    corrected_text: str
    changed: bool
    change_summary: str
    diff: OcrCorrectionDiff
    character_error_rate: float = Field(ge=0.0)
    word_error_rate: float = Field(ge=0.0)
    detected_medication_terms: list[str] = Field(default_factory=list)
    privacy_warnings: list[PrivacyWarning] = Field(default_factory=list)
    detected_possible_identifiers: list[str] = Field(default_factory=list)
    pharmacist_review_required: bool = True
    can_send_to_analysis: bool = True
    generated_at: str


class OcrCorrectionResponse(BaseModel):
    corrected_text: str
    pharmacist_review_required: bool = True
    correction_required: bool = False
    can_send_to_analysis: bool = True
    privacy_warnings: list[PrivacyWarning] = Field(default_factory=list)
    detected_possible_identifiers: list[str] = Field(default_factory=list)
    correction_audit: OcrCorrectionAudit | None = None


class OcrEvaluationResult(BaseModel):
    case_id: str
    provider_name: str = "mock_ocr_phase_2a"
    fixture_backed: bool = False
    passed: bool
    character_error_rate: float = Field(ge=0.0)
    word_error_rate: float = Field(ge=0.0)
    token_overlap_score: float = Field(ge=0.0, le=1.0)
    medication_detection_hit: bool
    privacy_warning_match: bool
    output_unverified: bool = True
    detected_possible_identifiers: list[str] = Field(default_factory=list)
    expected_possible_identifiers: list[str] = Field(default_factory=list)
    notes: str | None = None
