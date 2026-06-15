from typing import Literal

from pydantic import BaseModel, Field


ReviewStatus = Literal["draft", "pharmacist_reviewed", "approved_for_demo", "disabled"]
SourceStatus = Literal[
    "placeholder_educational",
    "pharmacist_supplied",
    "public_reference_pending_review",
    "validated_reference",
]
IssueSeverity = Literal["info", "warning", "error"]


class DrugRegistryEntry(BaseModel):
    drug_id: str
    generic_name: str
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

