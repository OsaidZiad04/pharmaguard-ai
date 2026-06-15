from app.rag.retriever import retrieve_contexts


def test_retriever_returns_relevant_chunks_for_paracetamol() -> None:
    contexts = retrieve_contexts("paracetamol 500mg counseling", top_k=5)

    assert contexts
    assert all(context.drug_name.lower() == "paracetamol" for context in contexts)
    assert any(context.section_title == "General Counseling Points" for context in contexts)


def test_retriever_returns_empty_context_for_unknown_drug() -> None:
    contexts = retrieve_contexts("xyzmed 10mg counseling", top_k=5)

    assert contexts == []


def test_retriever_returns_relevant_chunks_for_new_profiles() -> None:
    queries = {
        "cetirizine antihistamine counseling": "cetirizine",
        "loratadine allergy product counseling": "loratadine",
        "omeprazole acid symptom safety notes": "omeprazole",
        "salbutamol inhaler technique counseling": "salbutamol",
    }

    for query, expected_drug in queries.items():
        contexts = retrieve_contexts(query, top_k=5)

        assert contexts
        assert all(context.drug_name.lower() == expected_drug for context in contexts)


def test_retriever_uses_conservative_aliases_only() -> None:
    ventolin_contexts = retrieve_contexts("ventolin inhaler technique review", top_k=5)
    condition_only_contexts = retrieve_contexts("allergic rhinitis counseling options", top_k=5)

    assert ventolin_contexts
    assert all(context.drug_name.lower() == "salbutamol" for context in ventolin_contexts)
    assert condition_only_contexts == []
