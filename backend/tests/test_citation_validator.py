from app.rag.citation_validator import validate_generated_citations, validate_retrieved_chunks
from app.rag.generator import generate_grounded_answer
from app.rag.retriever import retrieve_contexts


def test_citation_validator_accepts_real_retrieved_sources() -> None:
    contexts = retrieve_contexts("paracetamol counseling", top_k=5)
    answer = generate_grounded_answer("paracetamol counseling", contexts)

    chunk_report = validate_retrieved_chunks(contexts)
    citation_report = validate_generated_citations(answer, contexts)

    assert chunk_report.valid is True
    assert citation_report.valid is True


def test_citation_validator_rejects_fabricated_source_reference() -> None:
    contexts = retrieve_contexts("paracetamol counseling", top_k=5)
    answer = (
        "Draft support only for pharmacist review.\n\n"
        "## Retrieved Sources\n"
        "- fabricated.md | Imaginary Section | fake:chunk | score 0.9900"
    )

    report = validate_generated_citations(answer, contexts)

    assert report.valid is False
    assert any("not retrieved" in error for error in report.errors)


def test_citation_validator_rejects_empty_context_source_claims() -> None:
    answer = (
        "insufficient knowledge base context. Draft support only. "
        "Pharmacist review required.\n\n"
        "## Retrieved Sources\n"
        "- paracetamol.md | Overview | paracetamol:overview:0-0 | score 0.1000"
    )

    report = validate_generated_citations(answer, [])

    assert report.valid is False
    assert any("no context" in error for error in report.errors)
