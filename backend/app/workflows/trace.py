from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


TraceStepStatus = Literal["pending", "completed", "blocked", "skipped", "failed"]
TraceFinalStatus = Literal["completed", "completed_with_warnings", "blocked", "failed"]
SafetyFlagSeverity = Literal["info", "warning", "critical"]


class WorkflowSafetyFlag(BaseModel):
    code: str
    severity: SafetyFlagSeverity = "info"
    step_name: str
    summary: str


class WorkflowTraceStep(BaseModel):
    step_name: str
    status: TraceStepStatus
    summary: str
    input_reference_type: str
    output_reference_type: str
    safety_notes: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class PharmacistReviewRecord(BaseModel):
    review_required: bool = True
    correction_required: bool = True
    correction_completed: bool = False
    corrected_text_used_for_analysis: bool = False
    reviewer_role: str = "pharmacist"
    notes: str


class WorkflowTrace(BaseModel):
    trace_id: str
    case_id: str
    created_at: str
    input_mode: str
    provider_name: str
    synthetic_trace: bool = True
    contains_real_patient_data: bool = False
    stores_raw_image_bytes: bool = False
    steps: list[WorkflowTraceStep] = Field(default_factory=list)
    safety_flags: list[WorkflowSafetyFlag] = Field(default_factory=list)
    pharmacist_review_required: bool = True
    pharmacist_review_record: PharmacistReviewRecord
    final_status: TraceFinalStatus
