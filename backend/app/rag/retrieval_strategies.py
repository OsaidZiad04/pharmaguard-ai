from __future__ import annotations

from dataclasses import replace
import re
from typing import Literal

from app.kb.governance import governance_metadata_for_entry
from app.kb.registry import get_drug_registry, normalize_drug_term
from app.rag.chunker import DocumentChunk, load_drug_profile_chunks
from app.rag.retriever import RetrievedContext, retrieve_contexts


RetrievalStrategyName = Literal[
    "existing_default",
    "current_tfidf",
    "lexical_overlap",
    "metadata_boosted",
    "hybrid_local",
]

AVAILABLE_STRATEGIES: tuple[RetrievalStrategyName, ...] = (
    "existing_default",
    "lexical_overlap",
    "metadata_boosted",
    "hybrid_local",
)

MIN_LEXICAL_SCORE = 0.04


def retrieve_with_strategy(
    query: str,
    strategy_name: RetrievalStrategyName = "existing_default",
    top_k: int = 5,
    medication_name: str | None = None,
) -> list[RetrievedContext]:
    """Run a local retrieval strategy without changing the production retriever."""
    if strategy_name in {"existing_default", "current_tfidf"}:
        contexts = retrieve_contexts(
            query=query,
            top_k=top_k,
            medication_name=medication_name,
        )
        return [
            replace(
                context,
                strategy_name=strategy_name,
                score_explanation=(
                    "Existing medication-aware TF-IDF retrieval with the current "
                    "production relevance threshold."
                ),
            )
            for context in contexts
        ]

    if strategy_name == "lexical_overlap":
        return _lexical_overlap_retrieval(query, top_k, medication_name)

    if strategy_name == "metadata_boosted":
        return _metadata_boosted_retrieval(query, top_k, medication_name)

    if strategy_name == "hybrid_local":
        return _hybrid_local_retrieval(query, top_k, medication_name)

    raise ValueError(f"Unsupported retrieval strategy: {strategy_name}")


def _lexical_overlap_retrieval(
    query: str,
    top_k: int,
    medication_name: str | None,
) -> list[RetrievedContext]:
    return _rank_chunks(
        query=query,
        top_k=top_k,
        medication_name=medication_name,
        strategy_name="lexical_overlap",
        metadata_boost=False,
    )


def _metadata_boosted_retrieval(
    query: str,
    top_k: int,
    medication_name: str | None,
) -> list[RetrievedContext]:
    return _rank_chunks(
        query=query,
        top_k=top_k,
        medication_name=medication_name,
        strategy_name="metadata_boosted",
        metadata_boost=True,
    )


def _hybrid_local_retrieval(
    query: str,
    top_k: int,
    medication_name: str | None,
) -> list[RetrievedContext]:
    default_contexts = retrieve_with_strategy(
        query=query,
        strategy_name="existing_default",
        top_k=top_k,
        medication_name=medication_name,
    )
    metadata_contexts = retrieve_with_strategy(
        query=query,
        strategy_name="metadata_boosted",
        top_k=top_k,
        medication_name=medication_name,
    )

    merged: dict[str, RetrievedContext] = {}
    for context in default_contexts:
        merged[context.chunk_id] = replace(
            context,
            strategy_name="hybrid_local",
            score_explanation=(
                "Hybrid local score using existing TF-IDF result priority plus "
                "metadata-aware lexical fallback."
            ),
        )

    for context in metadata_contexts:
        if context.chunk_id not in merged:
            merged[context.chunk_id] = replace(
                context,
                strategy_name="hybrid_local",
                score=round(context.score * 0.95, 4),
                score_explanation=(
                    "Hybrid local fallback from metadata-boosted lexical overlap."
                ),
            )

    return sorted(
        merged.values(),
        key=lambda context: context.score,
        reverse=True,
    )[:top_k]


def _rank_chunks(
    query: str,
    top_k: int,
    medication_name: str | None,
    strategy_name: RetrievalStrategyName,
    metadata_boost: bool,
) -> list[RetrievedContext]:
    target_drug = _resolve_target_drug(query, medication_name)
    if target_drug is None:
        return []

    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    chunks = [
        chunk
        for chunk in load_drug_profile_chunks()
        if normalize_drug_term(chunk.metadata["drug_name"]) == target_drug
    ]
    ranked: list[tuple[float, DocumentChunk, str]] = []
    for chunk in chunks:
        score, explanation = _score_chunk(
            query_tokens=query_tokens,
            chunk=chunk,
            metadata_boost=metadata_boost,
        )
        if score >= MIN_LEXICAL_SCORE:
            ranked.append((score, chunk, explanation))

    contexts: list[RetrievedContext] = []
    for score, chunk, explanation in sorted(ranked, key=lambda item: item[0], reverse=True)[
        :top_k
    ]:
        metadata = chunk.metadata
        governance_metadata = _governance_metadata_for_drug(target_drug)
        contexts.append(
            RetrievedContext(
                chunk_id=metadata["chunk_id"],
                drug_name=metadata["drug_name"],
                source_file=metadata["source_file"],
                section_title=metadata["section_title"],
                text=chunk.text,
                score=round(score, 4),
                strategy_name=strategy_name,
                score_explanation=explanation,
                **governance_metadata,
            )
        )
    return contexts


def _score_chunk(
    query_tokens: set[str],
    chunk: DocumentChunk,
    metadata_boost: bool,
) -> tuple[float, str]:
    chunk_tokens = _tokens(
        f"{chunk.metadata['drug_name']} {chunk.metadata['section_title']} {chunk.text}"
    )
    overlap = query_tokens.intersection(chunk_tokens)
    base_score = len(overlap) / max(len(query_tokens), 1)
    boosts: list[str] = []

    if metadata_boost:
        section_title = chunk.metadata["section_title"].lower()
        if "counsel" in query_tokens and "counsel" in section_title:
            base_score += 0.18
            boosts.append("section counseling boost")
        if "safety" in query_tokens and "safety" in section_title:
            base_score += 0.18
            boosts.append("section safety boost")
        if "overview" in query_tokens and "overview" in section_title:
            base_score += 0.12
            boosts.append("section overview boost")
        if normalize_drug_term(chunk.metadata["drug_name"]) in query_tokens:
            base_score += 0.08
            boosts.append("drug metadata boost")

    if not boosts:
        boosts.append("lexical token overlap")
    return min(base_score, 1.0), ", ".join(boosts)


def _resolve_target_drug(query: str, medication_name: str | None) -> str | None:
    try:
        registry = get_drug_registry()
    except (FileNotFoundError, ValueError):
        return None

    if medication_name:
        resolved = registry.resolve_drug_name(medication_name)
        return normalize_drug_term(resolved) if resolved else None

    normalized_query = normalize_drug_term(query)
    candidates: list[tuple[int, str]] = []
    for entry in registry.list_enabled_drugs():
        terms = [entry.generic_name, *entry.aliases]
        for term in terms:
            normalized_term = normalize_drug_term(term)
            if _contains_term(normalized_query, normalized_term):
                candidates.append((len(normalized_term), normalize_drug_term(entry.generic_name)))

    if not candidates:
        return None
    return sorted(candidates, reverse=True)[0][1]


def _governance_metadata_for_drug(normalized_drug_name: str) -> dict:
    try:
        registry = get_drug_registry()
    except (FileNotFoundError, ValueError):
        return {}

    entry = registry.lookup_by_generic_name(normalized_drug_name)
    return governance_metadata_for_entry(entry) if entry else {}


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalize_drug_term(value))
        if len(token) > 1
    }


def _contains_term(normalized_text: str, normalized_term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, normalized_text) is not None
