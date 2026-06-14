from app.rag.retriever import retrieve_contexts


def test_retriever_returns_relevant_chunks_for_paracetamol() -> None:
    contexts = retrieve_contexts("paracetamol 500mg counseling", top_k=5)

    assert contexts
    assert all(context.drug_name.lower() == "paracetamol" for context in contexts)
    assert any(context.section_title == "General Counseling Points" for context in contexts)


def test_retriever_returns_empty_context_for_unknown_drug() -> None:
    contexts = retrieve_contexts("xyzmed 10mg counseling", top_k=5)

    assert contexts == []
