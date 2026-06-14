import math
from dataclasses import dataclass
from typing import Any

from app.rag.chunker import DocumentChunk


@dataclass(frozen=True)
class VectorSearchResult:
    chunk: DocumentChunk
    score: float


class InMemoryVectorStore:
    """Local in-memory vector index for Phase 1 RAG."""

    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []
        self._vectors: Any | None = None

    @property
    def chunks(self) -> list[DocumentChunk]:
        return self._chunks

    def build(self, chunks: list[DocumentChunk], vectors: Any) -> None:
        self._chunks = chunks
        self._vectors = vectors

    def search(self, query_vector: Any, top_k: int = 5) -> list[VectorSearchResult]:
        if not self._chunks or self._vectors is None:
            return []

        scores = _similarity_scores(query_vector, self._vectors)
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        return [
            VectorSearchResult(
                chunk=self._chunks[index],
                score=round(float(scores[index]), 4),
            )
            for index in ranked_indices
        ]


def _similarity_scores(query_vector: Any, matrix: Any) -> list[float]:
    if hasattr(matrix, "dot") and hasattr(query_vector, "T"):
        raw_scores = matrix.dot(query_vector.T)
        if hasattr(raw_scores, "toarray"):
            return raw_scores.toarray().ravel().tolist()
        return list(raw_scores)

    query = _as_vector(query_vector[0] if query_vector and isinstance(query_vector[0], list) else query_vector)
    return [_cosine_similarity(query, _as_vector(row)) for row in matrix]


def _as_vector(value: Any) -> list[float]:
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
