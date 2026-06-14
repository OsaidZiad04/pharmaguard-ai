from app.rag.generator import generate_grounded_answer
from app.rag.retriever import RetrievedContext


def test_generator_marks_unavailable_sections_instead_of_inventing() -> None:
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

    assert "Not available in current knowledge base." in answer
    assert "Retrieved Sources" in answer
    assert "Draft support only for pharmacist review" in answer
