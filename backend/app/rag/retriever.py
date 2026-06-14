from app.rag.chunker import DocumentChunk
from app.rag.embedder import MockEmbedder
from app.rag.vector_store import InMemoryVectorStore


class Retriever:
    """Retrieve top-k chunks for a query.

    TODO: Add query rewriting, metadata filtering, and citation tracking.
    """

    def __init__(self, embedder: MockEmbedder, vector_store: InMemoryVectorStore) -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 3) -> list[DocumentChunk]:
        query_embedding = self.embedder.embed(query)
        return self.vector_store.search(query_embedding, top_k=top_k)
