import math
from dataclasses import dataclass

from app.rag.chunker import DocumentChunk


@dataclass
class VectorRecord:
    chunk: DocumentChunk
    embedding: list[float]


class InMemoryVectorStore:
    """Small placeholder vector store for tests and demos.

    TODO: Replace with persistent vector storage and source metadata filters.
    """

    def __init__(self) -> None:
        self._records: list[VectorRecord] = []

    def add(self, chunk: DocumentChunk, embedding: list[float]) -> None:
        self._records.append(VectorRecord(chunk=chunk, embedding=embedding))

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[DocumentChunk]:
        ranked = sorted(
            self._records,
            key=lambda record: _cosine_similarity(query_embedding, record.embedding),
            reverse=True,
        )
        return [record.chunk for record in ranked[:top_k]]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
