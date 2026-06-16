from app.rag.retriever import retrieve_contexts


def test_retriever_returns_relevant_chunks_for_paracetamol() -> None:
    contexts = retrieve_contexts("paracetamol 500mg counseling", top_k=5)

    assert contexts
    assert all(context.drug_name.lower() == "paracetamol" for context in contexts)
    assert any(context.section_title == "General Counseling Points" for context in contexts)
    assert all(context.source_status == "placeholder_educational" for context in contexts)
    assert all(context.review_status == "draft" for context in contexts)
    assert all(context.clinical_validation_status == "not_validated" for context in contexts)
    assert all(context.requires_pharmacist_review is True for context in contexts)
    assert all(context.patient_facing_allowed is False for context in contexts)


def test_retriever_returns_empty_context_for_unknown_drug() -> None:
    contexts = retrieve_contexts("xyzmed 10mg counseling", top_k=5)

    assert contexts == []


def test_retriever_returns_relevant_chunks_for_new_profiles() -> None:
    queries = {
        "cetirizine antihistamine counseling": "cetirizine",
        "loratadine allergy product counseling": "loratadine",
        "omeprazole acid symptom safety notes": "omeprazole",
        "salbutamol inhaler technique counseling": "salbutamol",
        "metformin formulation counseling": "metformin",
        "amlodipine swelling dizziness safety notes": "amlodipine",
        "levothyroxine timing supplements counseling": "levothyroxine",
        "azithromycin allergy duration counseling": "azithromycin",
        "simvastatin muscle concerns counseling": "simvastatin",
        "diclofenac topical oral formulation safety": "diclofenac",
        "esomeprazole duration counseling": "esomeprazole",
        "aspirin bleeding concerns counseling": "aspirin",
    }

    for query, expected_drug in queries.items():
        contexts = retrieve_contexts(query, top_k=5)

        assert contexts
        assert all(context.drug_name.lower() == expected_drug for context in contexts)


def test_retriever_uses_conservative_aliases_only() -> None:
    ventolin_contexts = retrieve_contexts("ventolin inhaler technique review", top_k=5)
    glucophage_contexts = retrieve_contexts("glucophage formulation counseling", top_k=5)
    nexium_contexts = retrieve_contexts("nexium duration counseling", top_k=5)
    condition_only_contexts = retrieve_contexts("allergic rhinitis counseling options", top_k=5)
    broad_condition_contexts = retrieve_contexts("diabetes counseling options", top_k=5)

    assert ventolin_contexts
    assert all(context.drug_name.lower() == "salbutamol" for context in ventolin_contexts)
    assert glucophage_contexts
    assert all(context.drug_name.lower() == "metformin" for context in glucophage_contexts)
    assert nexium_contexts
    assert all(context.drug_name.lower() == "esomeprazole" for context in nexium_contexts)
    assert condition_only_contexts == []
    assert broad_condition_contexts == []
