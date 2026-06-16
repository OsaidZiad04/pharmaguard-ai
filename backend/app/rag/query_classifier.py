from __future__ import annotations

from dataclasses import dataclass, field
import re

from app.kb.registry import get_drug_registry, normalize_drug_term


@dataclass(frozen=True)
class QueryClassification:
    query_type: str
    detected_medication_terms: list[str] = field(default_factory=list)
    missing_fields_requested: list[str] = field(default_factory=list)
    risk_level: str = "low"
    pharmacist_review_required: bool = True
    notes: list[str] = field(default_factory=list)


COUNSELING_TERMS = {"counsel", "counseling", "advice", "explain", "patient"}
SAFETY_TERMS = {
    "safety",
    "warning",
    "warnings",
    "allergy",
    "allergies",
    "interaction",
    "interactions",
    "contraindication",
    "contraindications",
    "pregnancy",
}
DOSE_TERMS = {
    "dose",
    "dosage",
    "dosing",
    "frequency",
    "duration",
    "route",
    "mg",
    "mcg",
    "how often",
    "exact",
}
LOOKUP_TERMS = {"lookup", "overview", "information", "info", "profile", "uses"}
MULTI_TERMS = {"multiple", "together", "combined", "combination", "both"}
UNKNOWN_MEDICATION_PATTERN = re.compile(
    r"\b(?:medication|drug|medicine|rx)\s*:\s*([a-z][a-z0-9-]{3,})",
    flags=re.IGNORECASE,
)


def classify_query(query: str) -> QueryClassification:
    normalized_query = normalize_drug_term(query)
    tokens = set(re.findall(r"[a-z0-9]+", normalized_query))
    detected_terms = _detected_medication_terms(normalized_query)
    missing_fields = _requested_fields(normalized_query)
    notes: list[str] = []

    if not detected_terms:
        if _looks_like_unknown_medication_query(query):
            return QueryClassification(
                query_type="unsupported_or_unknown",
                detected_medication_terms=[],
                missing_fields_requested=missing_fields,
                risk_level="high",
                pharmacist_review_required=True,
                notes=[
                    "Medication-like wording was present, but no supported medication was detected."
                ],
            )
        return QueryClassification(
            query_type="general_or_ambiguous",
            detected_medication_terms=[],
            missing_fields_requested=missing_fields,
            risk_level="medium",
            pharmacist_review_required=True,
            notes=["No explicit supported medication term detected."],
        )

    if _contains_phrase(normalized_query, MULTI_TERMS) or len(detected_terms) > 1:
        query_type = "multiple_medication_review"
        risk_level = "high"
        notes.append("Multiple medication terms or review wording detected.")
    elif _contains_phrase(normalized_query, SAFETY_TERMS):
        query_type = "safety_check"
        risk_level = "high" if {"interaction", "contraindication"}.intersection(tokens) else "medium"
        notes.append("Safety-oriented wording detected.")
    elif _contains_phrase(normalized_query, DOSE_TERMS):
        query_type = "dose_frequency_check"
        risk_level = "high"
        notes.append("Dose, frequency, route, or duration wording detected.")
    elif _contains_phrase(normalized_query, COUNSELING_TERMS):
        query_type = "counseling_request"
        risk_level = "medium"
        notes.append("Counseling request wording detected.")
    elif detected_terms and _contains_phrase(normalized_query, LOOKUP_TERMS):
        query_type = "drug_lookup"
        risk_level = "low"
        notes.append("Supported medication lookup wording detected.")
    elif detected_terms:
        query_type = "drug_lookup"
        risk_level = "low"
        notes.append("Supported medication term detected.")

    return QueryClassification(
        query_type=query_type,
        detected_medication_terms=detected_terms,
        missing_fields_requested=missing_fields,
        risk_level=risk_level,
        pharmacist_review_required=True,
        notes=notes,
    )


def _detected_medication_terms(normalized_query: str) -> list[str]:
    try:
        registry = get_drug_registry()
    except (FileNotFoundError, ValueError):
        return []

    detected: dict[str, str] = {}
    for entry in registry.list_enabled_drugs():
        canonical = normalize_drug_term(entry.generic_name)
        for term in [entry.generic_name, *entry.aliases]:
            normalized_term = normalize_drug_term(term)
            if _contains_term(normalized_query, normalized_term):
                detected[canonical] = canonical
    return sorted(detected.values())


def _requested_fields(normalized_query: str) -> list[str]:
    fields = []
    if "dose" in normalized_query or "dosage" in normalized_query or re.search(r"\bmg\b", normalized_query):
        fields.append("dose")
    if "frequency" in normalized_query or "how often" in normalized_query:
        fields.append("frequency")
    if "duration" in normalized_query or "how long" in normalized_query:
        fields.append("duration")
    if "route" in normalized_query or "oral" in normalized_query or "topical" in normalized_query:
        fields.append("route")
    return fields


def _looks_like_unknown_medication_query(query: str) -> bool:
    lowered = query.lower()
    if UNKNOWN_MEDICATION_PATTERN.search(query):
        return True
    if re.search(r"\b[a-z][a-z0-9-]{3,}\s+\d+\s?(?:mg|mcg|g|ml)\b", lowered):
        return True
    return any(term in lowered for term in ("unknown", "unsupported", "medication", "drug", "rx"))


def _contains_phrase(normalized_query: str, phrases: set[str]) -> bool:
    return any(phrase in normalized_query for phrase in phrases)


def _contains_term(normalized_text: str, normalized_term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, normalized_text) is not None
