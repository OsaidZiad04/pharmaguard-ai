from typing import Literal

from pydantic import BaseModel, Field


ReviewStatus = Literal[
    "draft",
    "pending_review",
    "reviewed",
    "rejected",
    "pharmacist_reviewed",
    "approved_for_demo",
    "disabled",
]
SourceStatus = Literal[
    "placeholder_educational",
    "trusted_source_pending",
    "trusted_source_ready",
    "pharmacist_reviewed",
    "pharmacist_supplied",
    "public_reference_pending_review",
    "validated_reference",
]
ClinicalValidationStatus = Literal[
    "not_validated",
    "engineering_only",
    "pharmacist_reviewed",
]
IssueSeverity = Literal["info", "warning", "error"]


class DrugRegistryEntry(BaseModel):
    drug_id: str
    profile_id: str | None = None
    generic_name: str
    canonical_name: str | None = None
    display_name: str
    profile_file: str
    aliases: list[str] = Field(default_factory=list)
    drug_class_general: str
    common_context_tags: list[str] = Field(default_factory=list)
    review_status: ReviewStatus = "draft"
    reviewed_by: str | None = None
    last_reviewed: str | None = None
    source_status: SourceStatus = "placeholder_educational"
    source_notes: str
    safety_notes: list[str] = Field(default_factory=list)
    enabled_for_rag: bool = True
    clinical_validation_status: ClinicalValidationStatus = "not_validated"
    requires_pharmacist_review: bool = True
    patient_facing_allowed: bool = False
    counseling_draft_allowed: bool = True
    source_refs: list[str] = Field(default_factory=list)
    last_reviewed_at: str | None = None
    reviewed_by_role: str | None = None
    notes: str | None = None


class DrugRegistry(BaseModel):
    drugs: list[DrugRegistryEntry]


class DrugProfileValidationIssue(BaseModel):
    severity: IssueSeverity
    code: str
    message: str
    drug_id: str | None = None
    profile_file: str | None = None


class DrugProfileValidationReport(BaseModel):
    valid: bool
    issues: list[DrugProfileValidationIssue] = Field(default_factory=list)
    missing_required_fields: dict[str, list[str]] = Field(default_factory=dict)
    missing_required_sections: dict[str, list[str]] = Field(default_factory=dict)
    alias_conflicts: dict[str, list[str]] = Field(default_factory=dict)
    disabled_profiles: list[str] = Field(default_factory=list)
    unreviewed_profiles: list[str] = Field(default_factory=list)


class KnowledgeBaseCoverageReport(BaseModel):
    total_profiles: int
    total_enabled_profiles: int
    total_aliases: int
    profiles_by_review_status: dict[str, int] = Field(default_factory=dict)
    profiles_by_source_status: dict[str, int] = Field(default_factory=dict)
    validation_report: DrugProfileValidationReport


class SourceCatalogEntry(BaseModel):
    source_category: str
    allowed_for_clinical_use: bool
    requires_pharmacist_review: bool
    requires_url_or_document_id: bool
    requires_last_reviewed_at: bool
    notes: str


class SourceCatalog(BaseModel):
    source_categories: list[SourceCatalogEntry]


class KnowledgeBaseGovernanceReport(BaseModel):
    valid: bool
    total_profiles: int
    enabled_for_rag_profiles: int
    profiles_by_source_status: dict[str, int] = Field(default_factory=dict)
    profiles_by_review_status: dict[str, int] = Field(default_factory=dict)
    profiles_by_clinical_validation_status: dict[str, int] = Field(default_factory=dict)
    patient_facing_allowed_count: int
    counseling_draft_allowed_count: int
    pharmacist_review_required_count: int
    source_catalog_categories: list[str] = Field(default_factory=list)
    blocking_issues: list[DrugProfileValidationIssue] = Field(default_factory=list)
    warnings: list[DrugProfileValidationIssue] = Field(default_factory=list)
