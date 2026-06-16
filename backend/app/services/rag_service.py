from app.rag.citation_validator import validate_generated_citations
from app.rag.generator import (
    INSUFFICIENT_CONTEXT_MESSAGE,
    build_rag_card_sections,
    generate_counseling_draft,
    generate_grounded_answer,
)
from app.rag.retriever import RetrievedContext, retrieve_contexts
from app.schemas.rag import RagDrugCard, RagQueryResponse, RetrievedChunk


def query_local_knowledge_base(query: str, top_k: int = 5) -> RagQueryResponse:
    contexts = retrieve_contexts(query=query, top_k=top_k)
    grounded_answer = generate_grounded_answer(query, contexts)
    retrieved_chunks = [_to_retrieved_chunk(context) for context in contexts]
    grounded_answer = _answer_with_valid_citations(grounded_answer, retrieved_chunks)

    return RagQueryResponse(
        query=query,
        retrieved_chunks=retrieved_chunks,
        grounded_answer=grounded_answer,
        review_required=True,
        insufficient_context=_is_insufficient(grounded_answer),
    )


def build_rag_drug_card(drug_name: str, top_k: int = 8) -> RagDrugCard:
    query = (
        f"{drug_name} overview common uses general counseling points "
        "safety notes pharmacist checks patient questions"
    )
    contexts = retrieve_contexts(
        query=query,
        top_k=top_k,
        medication_name=drug_name,
    )
    grounded_answer = generate_grounded_answer(query, contexts)
    retrieved_sources = [_to_retrieved_chunk(context) for context in contexts]
    grounded_answer = _answer_with_valid_citations(grounded_answer, retrieved_sources)
    sections = build_rag_card_sections(contexts)

    return RagDrugCard(
        name=drug_name,
        overview=sections["overview"],
        key_counseling_points=sections["key_counseling_points"],
        safety_notes=sections["safety_notes"],
        pharmacist_checks=sections["pharmacist_checks"],
        retrieved_sources=retrieved_sources,
        grounded_answer=grounded_answer,
        insufficient_context=_is_insufficient(grounded_answer),
        pharmacist_review_required=True,
    )


def build_grounded_counseling_note(
    medication_name: str,
    strength: str | None,
    directions: str | None,
    additional_notes: str | None = None,
    top_k: int = 8,
) -> tuple[str, list[RetrievedChunk], bool]:
    query = f"{medication_name} general counseling points safety notes patient questions"
    contexts = retrieve_contexts(
        query=query,
        top_k=top_k,
        medication_name=medication_name,
    )
    note = generate_counseling_draft(
        medication_name=medication_name,
        strength=strength,
        directions=directions,
        contexts=contexts,
        additional_notes=additional_notes,
    )
    retrieved_chunks = [_to_retrieved_chunk(context) for context in contexts]
    note = _answer_with_valid_citations(note, retrieved_chunks)
    return (
        note,
        retrieved_chunks,
        _is_insufficient(note),
    )


def _to_retrieved_chunk(context: RetrievedContext) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=context.chunk_id,
        drug_name=context.drug_name,
        source_file=context.source_file,
        section_title=context.section_title,
        text=context.text,
        score=context.score,
        source_status=context.source_status,
        review_status=context.review_status,
        clinical_validation_status=context.clinical_validation_status,
        requires_pharmacist_review=context.requires_pharmacist_review,
        patient_facing_allowed=context.patient_facing_allowed,
        counseling_draft_allowed=context.counseling_draft_allowed,
    )


def _is_insufficient(answer: str) -> bool:
    return INSUFFICIENT_CONTEXT_MESSAGE in answer.lower()


def _answer_with_valid_citations(answer: str, chunks: list[RetrievedChunk]) -> str:
    report = validate_generated_citations(answer, chunks)
    if report.valid:
        return answer
    return (
        f"{INSUFFICIENT_CONTEXT_MESSAGE}. Citation validation failed, so the "
        "grounded answer was withheld. Pharmacist review required."
    )
