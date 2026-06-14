from dataclasses import dataclass
from functools import lru_cache

from app.rag.chunker import DocumentChunk, load_drug_profile_chunks
from app.rag.embedder import TfidfEmbedder
from app.rag.vector_store import InMemoryVectorStore

DEFAULT_MIN_RELEVANCE = 0.08


@dataclass(frozen=True)
class RetrievedContext:
    chunk_id: str
    drug_name: str
    source_file: str
    section_title: str
    text: str
    score: float


class LocalRagIndex:
    def __init__(self, min_relevance: float = DEFAULT_MIN_RELEVANCE) -> None:
        self.min_relevance = min_relevance
        self.embedder = TfidfEmbedder()
        self.vector_store = InMemoryVectorStore()
        self.chunks = load_drug_profile_chunks()
        self.known_drug_names = {
            chunk.metadata["drug_name"].lower() for chunk in self.chunks
        }

        if self.chunks:
            vectors = self.embedder.fit_transform(
                [_chunk_search_text(chunk) for chunk in self.chunks]
            )
            self.vector_store.build(self.chunks, vectors)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        medication_name: str | None = None,
    ) -> list[RetrievedContext]:
        if not query.strip() or not self.chunks:
            return []

        target_drug = self._resolve_drug_name(query, medication_name)
        if target_drug is None:
            return []

        query_vector = self.embedder.transform([query])
        raw_results = self.vector_store.search(query_vector, top_k=max(top_k * 3, top_k))
        contexts: list[RetrievedContext] = []

        for result in raw_results:
            metadata = result.chunk.metadata
            if metadata["drug_name"].lower() != target_drug:
                continue
            if result.score < self.min_relevance:
                continue

            contexts.append(
                RetrievedContext(
                    chunk_id=metadata["chunk_id"],
                    drug_name=metadata["drug_name"],
                    source_file=metadata["source_file"],
                    section_title=metadata["section_title"],
                    text=result.chunk.text,
                    score=result.score,
                )
            )

            if len(contexts) >= top_k:
                break

        return contexts

    def _resolve_drug_name(self, query: str, medication_name: str | None) -> str | None:
        if medication_name:
            normalized = medication_name.strip().lower()
            if normalized in self.known_drug_names:
                return normalized
            return None

        normalized_query = query.lower()
        matches = [
            drug_name
            for drug_name in self.known_drug_names
            if drug_name in normalized_query
        ]
        if not matches:
            return None
        return sorted(matches, key=len, reverse=True)[0]


@lru_cache
def get_local_rag_index() -> LocalRagIndex:
    return LocalRagIndex()


def retrieve_contexts(
    query: str,
    top_k: int = 5,
    medication_name: str | None = None,
) -> list[RetrievedContext]:
    return get_local_rag_index().retrieve(
        query=query,
        top_k=top_k,
        medication_name=medication_name,
    )


def _chunk_search_text(chunk: DocumentChunk) -> str:
    metadata = chunk.metadata
    return (
        f"{metadata['drug_name']} {metadata['section_title']} "
        f"{chunk.text}"
    )
