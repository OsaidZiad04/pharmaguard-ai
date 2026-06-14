import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_id: str
    text: str
    metadata: dict[str, str]


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def default_drug_profiles_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "drug_profiles"


def load_drug_profile_chunks(profiles_dir: Path | None = None) -> list[DocumentChunk]:
    """Load and chunk all local Markdown drug profiles."""
    root = profiles_dir or default_drug_profiles_dir()
    if not root.exists():
        return []

    chunks: list[DocumentChunk] = []
    for markdown_file in sorted(root.glob("*.md")):
        chunks.extend(chunk_markdown_file(markdown_file))
    return chunks


def chunk_markdown_file(markdown_file: Path) -> list[DocumentChunk]:
    text = markdown_file.read_text(encoding="utf-8")
    drug_name = _extract_drug_name(markdown_file, text)
    return chunk_markdown_text(
        text=text,
        drug_name=drug_name,
        source_file=markdown_file.name,
    )


def chunk_markdown_text(
    text: str,
    drug_name: str,
    source_file: str,
    max_chars: int = 750,
) -> list[DocumentChunk]:
    """Split Markdown by headings and paragraphs while preserving source metadata."""
    sections = _parse_sections(text)
    chunks: list[DocumentChunk] = []

    for section_index, section in enumerate(sections):
        section_title = section["title"]
        paragraphs = _paragraphs(section["body"])
        grouped_paragraphs = _group_paragraphs(paragraphs, max_chars=max_chars)

        for chunk_index, grouped in enumerate(grouped_paragraphs):
            chunk_id = (
                f"{_slug(drug_name)}:{_slug(section_title)}:"
                f"{section_index}-{chunk_index}"
            )
            chunk_text = "\n".join(grouped).strip()
            if not chunk_text:
                continue

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    source_id=source_file,
                    text=chunk_text,
                    metadata={
                        "drug_name": drug_name,
                        "source_file": source_file,
                        "section_title": section_title,
                        "chunk_id": chunk_id,
                    },
                )
            )

    return chunks


def chunk_document(source_id: str, text: str, max_chars: int = 750) -> list[DocumentChunk]:
    """Compatibility helper for generic text chunking."""
    return chunk_markdown_text(
        text=text,
        drug_name=Path(source_id).stem,
        source_file=source_id,
        max_chars=max_chars,
    )


def _parse_sections(text: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        heading_match = HEADING_PATTERN.match(line)

        if heading_match:
            if current_lines:
                sections.append(
                    {"title": current_title, "body": "\n".join(current_lines).strip()}
                )
                current_lines = []

            heading_level = len(heading_match.group(1))
            heading_title = heading_match.group(2).strip()
            if heading_level == 1:
                current_title = "Overview"
            else:
                current_title = heading_title
            continue

        current_lines.append(line)

    if current_lines:
        sections.append({"title": current_title, "body": "\n".join(current_lines).strip()})

    return [section for section in sections if section["body"]]


def _paragraphs(section_body: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []

    for line in section_body.splitlines():
        clean_line = line.strip()
        if not clean_line:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        current.append(clean_line)

    if current:
        paragraphs.append(" ".join(current).strip())

    return paragraphs


def _group_paragraphs(paragraphs: list[str], max_chars: int) -> list[list[str]]:
    groups: list[list[str]] = []
    current_group: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        projected_length = current_length + len(paragraph) + 1
        if current_group and projected_length > max_chars:
            groups.append(current_group)
            current_group = []
            current_length = 0

        current_group.append(paragraph)
        current_length += len(paragraph) + 1

    if current_group:
        groups.append(current_group)

    return groups


def _extract_drug_name(markdown_file: Path, text: str) -> str:
    for line in text.splitlines():
        heading_match = HEADING_PATTERN.match(line.strip())
        if heading_match and len(heading_match.group(1)) == 1:
            return heading_match.group(2).strip()
    return markdown_file.stem.replace("_", " ").replace("-", " ").title()


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "chunk"
