from app.rag.chunker import load_drug_profile_chunks


def test_chunker_loads_markdown_drug_profiles() -> None:
    chunks = load_drug_profile_chunks()

    drug_names = {chunk.metadata["drug_name"].lower() for chunk in chunks}
    section_titles = {chunk.metadata["section_title"] for chunk in chunks}

    assert {
        "paracetamol",
        "ibuprofen",
        "amoxicillin",
        "cetirizine",
        "loratadine",
        "omeprazole",
        "salbutamol",
        "metformin",
        "amlodipine",
        "levothyroxine",
        "azithromycin",
        "simvastatin",
        "diclofenac",
        "esomeprazole",
        "aspirin",
    }.issubset(drug_names)
    assert len(drug_names) >= 15
    assert "Knowledge Base Limitations" in section_titles
    assert "General Counseling Points" in section_titles
    assert all(chunk.metadata["source_file"].endswith(".md") for chunk in chunks)
