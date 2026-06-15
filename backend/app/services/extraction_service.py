import re

from app.utils.text_cleaning import normalize_whitespace

MEDICATION_ALIASES = {
    "paracetamol": "paracetamol",
    "acetaminophen": "paracetamol",
    "ibuprofen": "ibuprofen",
    "amoxicillin": "amoxicillin",
    "cetirizine": "cetirizine",
    "zyrtec": "cetirizine",
    "loratadine": "loratadine",
    "claritin": "loratadine",
    "omeprazole": "omeprazole",
    "prilosec": "omeprazole",
    "salbutamol": "salbutamol",
    "ventolin": "salbutamol",
}

STRENGTH_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|mL|%)"
    r"(?:\s?/\s?\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|mL))?\b"
)

DIRECTION_PATTERN = re.compile(
    r"\b(?:take|give|use|apply|inject|place)\b[^.:\n]*",
    flags=re.IGNORECASE,
)


def extract_medication_candidates(raw_text: str) -> list[dict]:
    """Return medication candidates from prescription text using mock rules.

    TODO: Replace rule matching with evaluated extraction models and a normalized
    drug vocabulary. This function must keep returning confidence metadata.
    """
    cleaned = normalize_whitespace(raw_text)
    if not cleaned:
        return []

    lower_text = cleaned.lower()
    candidates: list[dict] = []
    seen: set[str] = set()

    for alias, canonical_name in MEDICATION_ALIASES.items():
        match = re.search(rf"\b{re.escape(alias)}\b", lower_text)
        if not match or canonical_name in seen:
            continue

        source_text = _extract_source_text(cleaned, match.start(), match.end())
        strength = _extract_strength(source_text) or _extract_strength(cleaned)
        directions = _extract_directions(source_text) or _extract_directions(cleaned)

        candidates.append(
            {
                "name": canonical_name,
                "matched_text": alias,
                "strength": strength,
                "directions": directions,
                "source_text": source_text,
                "confidence": _estimate_confidence(strength, directions),
                "is_known": True,
            }
        )
        seen.add(canonical_name)

    return candidates


def _extract_strength(text: str) -> str | None:
    match = STRENGTH_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_directions(text: str) -> str | None:
    match = DIRECTION_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).strip()


def _extract_source_text(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_candidates = [index for index in (text.find(".", end), text.find("\n", end)) if index != -1]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1 : right].strip()


def _estimate_confidence(strength: str | None, directions: str | None) -> float:
    confidence = 0.9
    if not strength:
        confidence -= 0.12
    if not directions:
        confidence -= 0.12
    return round(max(confidence, 0.0), 2)
