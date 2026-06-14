from app.rag.chunker import load_drug_profile_chunks


def test_chunker_loads_markdown_drug_profiles() -> None:
    chunks = load_drug_profile_chunks()

    drug_names = {chunk.metadata["drug_name"].lower() for chunk in chunks}
    section_titles = {chunk.metadata["section_title"] for chunk in chunks}

    assert {"paracetamol", "ibuprofen", "amoxicillin"}.issubset(drug_names)
    assert "General Counseling Points" in section_titles
    assert all(chunk.metadata["source_file"].endswith(".md") for chunk in chunks)
