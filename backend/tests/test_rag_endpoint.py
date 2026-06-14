from fastapi.testclient import TestClient

from app.main import app


def test_rag_query_endpoint_returns_grounded_context() -> None:
    client = TestClient(app)

    response = client.post(
        "/rag/query",
        json={"query": "paracetamol 500mg counseling", "top_k": 5},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["review_required"] is True
    assert body["retrieved_chunks"]
    assert body["retrieved_chunks"][0]["source_file"].endswith(".md")
    assert "Retrieved Sources" in body["grounded_answer"]


def test_rag_query_endpoint_returns_insufficient_context_for_unknown() -> None:
    client = TestClient(app)

    response = client.post(
        "/rag/query",
        json={"query": "xyzmed 10mg counseling", "top_k": 5},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["retrieved_chunks"] == []
    assert body["insufficient_context"] is True
    assert "insufficient knowledge base context" in body["grounded_answer"]
