from app.rag.citation_validator import validate_generated_citations
from app.rag.evaluation import FINAL_ADVICE_FORBIDDEN_TERMS, load_eval_cases
from app.rag.generator import NOT_AVAILABLE_MESSAGE, generate_grounded_answer
from app.rag.retriever import RetrievedContext, retrieve_contexts
from app.services.rag_service import query_local_knowledge_base


def test_unknown_medication_returns_insufficient_context() -> None:
    response = query_local_knowledge_base("xyzmed 10mg counseling", top_k=5)

    assert response.review_required is True
    assert response.insufficient_context is True
    assert response.retrieved_chunks == []
    assert "insufficient knowledge base context" in response.grounded_answer


def test_weak_generic_query_does_not_retrieve_random_drug_chunks() -> None:
    contexts = retrieve_contexts("general counseling points and safety notes", top_k=5)

    assert contexts == []


def test_generator_marks_missing_sections_as_unavailable() -> None:
    contexts = [
        RetrievedContext(
            chunk_id="paracetamol:overview:0-0",
            drug_name="Paracetamol",
            source_file="paracetamol.md",
            section_title="Overview",
            text="Paracetamol is a medication commonly discussed in pharmacy settings for pain or fever support.",
            score=0.91,
        )
    ]

    answer = generate_grounded_answer("paracetamol counseling", contexts)

    assert NOT_AVAILABLE_MESSAGE in answer


def test_generated_answers_exclude_forbidden_eval_terms() -> None:
    for case in load_eval_cases():
        response = query_local_knowledge_base(case["query"], top_k=5)
        lowered_answer = response.grounded_answer.lower()

        for forbidden_term in case["must_not_include_terms"]:
            assert forbidden_term.lower() not in lowered_answer


def test_generated_answers_do_not_use_final_advice_language() -> None:
    response = query_local_knowledge_base("paracetamol counseling", top_k=5)
    lowered_answer = response.grounded_answer.lower()

    for forbidden_term in FINAL_ADVICE_FORBIDDEN_TERMS:
        assert forbidden_term not in lowered_answer
    assert "draft" in lowered_answer
    assert "pharmacist review" in lowered_answer


def test_pharmacist_review_required_remains_true() -> None:
    supported = query_local_knowledge_base("ibuprofen safety counseling", top_k=5)
    unknown = query_local_knowledge_base("unknownmed counseling", top_k=5)

    assert supported.review_required is True
    assert unknown.review_required is True


def test_generated_answer_citations_are_not_fabricated() -> None:
    contexts = retrieve_contexts("amoxicillin allergy counseling", top_k=5)
    answer = generate_grounded_answer("amoxicillin allergy counseling", contexts)
    report = validate_generated_citations(answer, contexts)

    assert report.valid is True
