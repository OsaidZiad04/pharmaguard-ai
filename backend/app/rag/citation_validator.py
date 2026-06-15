from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CitationReference:
    source_file: str
    section_title: str
    chunk_id: str


@dataclass
class CitationValidationReport:
    valid: bool
    errors: list[str] = field(default_factory=list)
    references: list[CitationReference] = field(default_factory=list)


def validate_retrieved_chunks(chunks: list[Any]) -> CitationValidationReport:
    errors: list[str] = []
    for index, chunk in enumerate(chunks):
        for field_name in ("chunk_id", "source_file", "section_title"):
            if not _field_value(chunk, field_name):
                errors.append(f"chunk[{index}] is missing {field_name}")

    return CitationValidationReport(valid=not errors, errors=errors)


def validate_generated_citations(
    generated_answer: str,
    retrieved_chunks: list[Any],
) -> CitationValidationReport:
    chunk_report = validate_retrieved_chunks(retrieved_chunks)
    errors = list(chunk_report.errors)
    references = extract_source_references(generated_answer)

    if not retrieved_chunks and references:
        errors.append("generated answer cites sources even though no context was retrieved")

    if not retrieved_chunks and "## Retrieved Sources" in generated_answer:
        errors.append("generated answer includes a Retrieved Sources section with no context")

    available_references = {
        (
            _field_value(chunk, "source_file"),
            _field_value(chunk, "section_title"),
            _field_value(chunk, "chunk_id"),
        )
        for chunk in retrieved_chunks
    }

    for reference in references:
        key = (reference.source_file, reference.section_title, reference.chunk_id)
        if key not in available_references:
            errors.append(
                "generated answer cites a source that was not retrieved: "
                f"{reference.source_file} | {reference.section_title} | {reference.chunk_id}"
            )

    if retrieved_chunks and not references:
        errors.append("generated answer has retrieved context but no source references")

    return CitationValidationReport(
        valid=not errors,
        errors=errors,
        references=references,
    )


def extract_source_references(generated_answer: str) -> list[CitationReference]:
    references: list[CitationReference] = []
    in_sources = False

    for raw_line in generated_answer.splitlines():
        line = raw_line.strip()
        if line == "## Retrieved Sources":
            in_sources = True
            continue
        if in_sources and line.startswith("## "):
            break
        if not in_sources or not line.startswith("- "):
            continue

        parts = [part.strip() for part in line[2:].split("|")]
        if len(parts) < 3:
            continue

        references.append(
            CitationReference(
                source_file=parts[0],
                section_title=parts[1],
                chunk_id=parts[2],
            )
        )

    return references


def _field_value(chunk: Any, field_name: str) -> str:
    value = getattr(chunk, field_name, None)
    if value is None and isinstance(chunk, dict):
        value = chunk.get(field_name)
    return str(value).strip() if value is not None else ""
