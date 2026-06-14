from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_id: str
    text: str
    metadata: dict[str, str]


def chunk_document(source_id: str, text: str, max_chars: int = 900) -> list[DocumentChunk]:
    """Split a document into rough text chunks.

    TODO: Replace with token-aware chunking and source section metadata.
    """
    chunks: list[DocumentChunk] = []
    clean_text = text.strip()
    if not clean_text:
        return chunks

    for index, start in enumerate(range(0, len(clean_text), max_chars)):
        chunk_text = clean_text[start : start + max_chars].strip()
        chunks.append(
            DocumentChunk(
                chunk_id=f"{source_id}:{index}",
                source_id=source_id,
                text=chunk_text,
                metadata={"chunk_index": str(index)},
            )
        )

    return chunks
