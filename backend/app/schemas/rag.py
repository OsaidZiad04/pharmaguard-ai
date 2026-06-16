from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    chunk_id: str
    drug_name: str
    source_file: str
    section_title: str
    text: str
    score: float = Field(ge=0.0)
    source_status: str | None = None
    review_status: str | None = None
    clinical_validation_status: str | None = None
    requires_pharmacist_review: bool | None = None
    patient_facing_allowed: bool | None = None
    counseling_draft_allowed: bool | None = None
    strategy_name: str | None = None
    score_explanation: str | None = None


class RagQueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)


class RagQueryResponse(BaseModel):
    query: str
    retrieved_chunks: list[RetrievedChunk]
    grounded_answer: str
    review_required: bool = True
    insufficient_context: bool = False
    retrieval_diagnostics: dict | None = None


class RagDrugCard(BaseModel):
    name: str
    overview: list[str] = Field(default_factory=list)
    key_counseling_points: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    pharmacist_checks: list[str] = Field(default_factory=list)
    retrieved_sources: list[RetrievedChunk] = Field(default_factory=list)
    grounded_answer: str
    insufficient_context: bool = False
    retrieval_diagnostics: dict | None = None
    source: str = "local_markdown_tfidf_rag"
    pharmacist_review_required: bool = True
