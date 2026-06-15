from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path

from app.rag.chunker import DocumentChunk, load_drug_profile_chunks
from app.rag.embedder import TfidfEmbedder
from app.rag.vector_store import InMemoryVectorStore

DEFAULT_MIN_RELEVANCE = 0.08
MOCK_INDEX_PATH = Path(__file__).resolve().parents[1] / "sample_data" / "mock_drug_index.json"


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
        self.alias_map = _load_alias_map(self.known_drug_names)

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
            if normalized in self.alias_map:
                return self.alias_map[normalized]
            return None

        normalized_query = query.lower()
        for alias, canonical_name in self.alias_map.items():
            if alias in normalized_query:
                return canonical_name

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


def _load_alias_map(known_drug_names: set[str]) -> dict[str, str]:
    if not MOCK_INDEX_PATH.exists():
        return {}

    with MOCK_INDEX_PATH.open("r", encoding="utf-8") as file:
        index = json.load(file)

    aliases: dict[str, str] = {}
    for canonical_name, profile in index.items():
        normalized_canonical = canonical_name.lower()
        if normalized_canonical not in known_drug_names:
            continue
        for alias in profile.get("aliases", []):
            aliases[alias.strip().lower()] = normalized_canonical
    return aliases
