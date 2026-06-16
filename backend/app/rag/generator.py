from app.rag.retriever import RetrievedContext

INSUFFICIENT_CONTEXT_MESSAGE = "insufficient knowledge base context"
NOT_AVAILABLE_MESSAGE = "Not available in current knowledge base."


SECTION_GROUPS = {
    "Medication Overview": {"Overview", "Common Uses"},
    "Key Counseling Points": {"General Counseling Points"},
    "Safety Notes": {"Safety Notes", "When to Refer to Pharmacist or Physician"},
    "Missing Context / Pharmacist Checks": {"Patient Questions to Ask"},
}


def generate_grounded_answer(query: str, contexts: list[RetrievedContext]) -> str:
    """Generate a pharmacist-facing draft using only retrieved local context."""
    if not contexts:
        return (
            f"{INSUFFICIENT_CONTEXT_MESSAGE}. Draft support only. Pharmacist review required. "
            "No medication-specific local Markdown context met the retrieval threshold."
        )

    lines = [
        "Draft support only for pharmacist review. This is not a final clinical decision.",
        "",
    ]

    for output_section, source_sections in SECTION_GROUPS.items():
        lines.append(f"## {output_section}")
        section_text = _texts_for_sections(contexts, source_sections)
        if section_text:
            lines.extend([f"- {text}" for text in section_text])
        else:
            lines.append(f"- {NOT_AVAILABLE_MESSAGE}")
        lines.append("")

    lines.append("## Retrieved Sources")
    lines.extend(_source_lines(contexts))

    return "\n".join(lines).strip()


def build_rag_card_sections(contexts: list[RetrievedContext]) -> dict[str, list[str]]:
    return {
        "overview": _texts_for_sections(contexts, {"Overview", "Common Uses"}),
        "key_counseling_points": _texts_for_sections(
            contexts,
            {"General Counseling Points"},
        ),
        "safety_notes": _texts_for_sections(
            contexts,
            {"Safety Notes", "When to Refer to Pharmacist or Physician"},
        ),
        "pharmacist_checks": _texts_for_sections(contexts, {"Patient Questions to Ask"}),
    }


def generate_counseling_draft(
    medication_name: str,
    strength: str | None,
    directions: str | None,
    contexts: list[RetrievedContext],
    additional_notes: str | None = None,
) -> str:
    if not contexts:
        return (
            f"{INSUFFICIENT_CONTEXT_MESSAGE}. Counseling draft cannot be grounded "
            "from the local Markdown knowledge base. Pharmacist review required."
        )

    sections = build_rag_card_sections(contexts)
    strength_text = strength or "strength not confirmed"
    directions_text = directions or "directions not confirmed"

    lines = [
        "Draft-only patient counseling support for pharmacist review.",
        "This is not a final clinical decision and must be verified by the pharmacist.",
        f"Medication confirmed by pharmacist: {medication_name} ({strength_text}).",
        f"Confirmed prescription directions: {directions_text}.",
        "",
        "## Key Counseling Points",
    ]
    lines.extend(_section_or_unavailable(sections["key_counseling_points"]))
    lines.extend(["", "## Safety Notes"])
    lines.extend(_section_or_unavailable(sections["safety_notes"]))
    lines.extend(["", "## Missing Context / Pharmacist Checks"])
    lines.extend(_section_or_unavailable(sections["pharmacist_checks"]))

    if additional_notes:
        lines.extend(["", f"Pharmacist note: {additional_notes.strip()}"])

    lines.extend(["", "## Retrieved Sources"])
    lines.extend(_source_lines(contexts))

    return "\n".join(lines).strip()


def _texts_for_sections(
    contexts: list[RetrievedContext],
    section_titles: set[str],
) -> list[str]:
    texts: list[str] = []
    for context in contexts:
        if context.section_title not in section_titles:
            continue
        texts.extend(_split_context_text(context.text))
    return _dedupe(texts)


def _split_context_text(text: str) -> list[str]:
    fragments: list[str] = []
    for raw_line in text.splitlines():
        clean_line = raw_line.strip()
        if not clean_line:
            continue
        if clean_line.startswith("- "):
            clean_line = clean_line[2:].strip()
        fragments.append(clean_line)
    return fragments


def _source_lines(contexts: list[RetrievedContext]) -> list[str]:
    source_lines = []
    for context in contexts:
        governance_tags = _governance_source_tags(context)
        source_lines.append(
            f"- {context.source_file} | {context.section_title} | "
            f"{context.chunk_id} | score {context.score:.4f}{governance_tags}"
        )
    return _dedupe(source_lines)


def _governance_source_tags(context: RetrievedContext) -> str:
    tags = []
    if context.source_status:
        tags.append(f"source_status {context.source_status}")
    if context.review_status:
        tags.append(f"review_status {context.review_status}")
    if context.clinical_validation_status:
        tags.append(f"clinical_validation_status {context.clinical_validation_status}")
    if context.requires_pharmacist_review is not None:
        tags.append(f"pharmacist_review_required {context.requires_pharmacist_review}")
    if not tags:
        return ""
    return " | " + " | ".join(tags)


def _section_or_unavailable(texts: list[str]) -> list[str]:
    if not texts:
        return [f"- {NOT_AVAILABLE_MESSAGE}"]
    return [f"- {text}" for text in texts]


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
