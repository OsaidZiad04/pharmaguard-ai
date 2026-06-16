from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.rag.query_classifier import classify_query


@dataclass(frozen=True)
class RetrievalDiagnosticReport:
    retrieval_status: str
    source_count: int
    unique_drug_count: int
    governance_warning_count: int
    pharmacist_review_required: bool
    insufficient_context: bool
    warnings: list[str] = field(default_factory=list)
    recommended_action: str = "Pharmacist review required."


def analyze_retrieval_result(
    query: str,
    retrieved_chunks: list[Any],
) -> RetrievalDiagnosticReport:
    warnings: list[str] = []
    classification = classify_query(query)
    source_count = len({_field(chunk, "source_file") for chunk in retrieved_chunks if _field(chunk, "source_file")})
    unique_drug_count = len({_field(chunk, "drug_name").lower() for chunk in retrieved_chunks if _field(chunk, "drug_name")})
    max_score = max((_float_field(chunk, "score") for chunk in retrieved_chunks), default=0.0)

    if not retrieved_chunks:
        warnings.append("No local knowledge-base context was retrieved.")
        if classification.query_type == "unsupported_or_unknown":
            warnings.append("Medication-like query has no supported local KB match.")
        if classification.query_type == "general_or_ambiguous":
            warnings.append("Query is general or ambiguous and should not map to an arbitrary medication.")
        return RetrievalDiagnosticReport(
            retrieval_status="insufficient",
            source_count=0,
            unique_drug_count=0,
            governance_warning_count=0,
            pharmacist_review_required=True,
            insufficient_context=True,
            warnings=warnings,
            recommended_action=(
                "Return insufficient knowledge-base context and ask the pharmacist to verify the medication."
            ),
        )

    if max_score < 0.12 or len(retrieved_chunks) == 1:
        retrieval_status = "weak"
        warnings.append("Retrieved context is sparse or low-scoring.")
    elif max_score < 0.25 or source_count == 1:
        retrieval_status = "moderate"
        if source_count == 1:
            warnings.append("Retrieved context comes from a single source file.")
    else:
        retrieval_status = "strong"

    if unique_drug_count > 1:
        warnings.append("Retrieved context mentions multiple medication profiles.")

    governance_warnings = detect_governance_risk_in_retrieval(retrieved_chunks)
    warnings.extend(governance_warnings)

    pharmacist_review_required = True
    if any(_bool_field(chunk, "requires_pharmacist_review") for chunk in retrieved_chunks):
        pharmacist_review_required = True
    if any(_field(chunk, "requires_pharmacist_review") == "" for chunk in retrieved_chunks):
        warnings.append("One or more chunks are missing pharmacist review metadata.")

    insufficient_context = retrieval_status == "insufficient"
    if retrieval_status == "weak":
        recommended_action = (
            "Treat retrieval as weak context. Keep output draft-only and require pharmacist verification."
        )
    elif governance_warnings:
        recommended_action = (
            "Show source governance warnings and keep pharmacist review mandatory."
        )
    else:
        recommended_action = "Use retrieved context as pharmacist-support draft only."

    return RetrievalDiagnosticReport(
        retrieval_status=retrieval_status,
        source_count=source_count,
        unique_drug_count=unique_drug_count,
        governance_warning_count=len(governance_warnings),
        pharmacist_review_required=pharmacist_review_required,
        insufficient_context=insufficient_context,
        warnings=warnings,
        recommended_action=recommended_action,
    )


def summarize_retrieval_quality(query: str, retrieved_chunks: list[Any]) -> dict[str, Any]:
    report = analyze_retrieval_result(query, retrieved_chunks)
    return {
        "retrieval_status": report.retrieval_status,
        "source_count": report.source_count,
        "unique_drug_count": report.unique_drug_count,
        "governance_warning_count": report.governance_warning_count,
        "pharmacist_review_required": report.pharmacist_review_required,
        "insufficient_context": report.insufficient_context,
        "warnings": report.warnings,
        "recommended_action": report.recommended_action,
    }


def detect_weak_retrieval(query: str, retrieved_chunks: list[Any]) -> bool:
    return analyze_retrieval_result(query, retrieved_chunks).retrieval_status in {
        "weak",
        "insufficient",
    }


def detect_governance_risk_in_retrieval(retrieved_chunks: list[Any]) -> list[str]:
    warnings: list[str] = []
    if not retrieved_chunks:
        return warnings

    if any(not _field(chunk, "source_status") for chunk in retrieved_chunks):
        warnings.append("Retrieved context is missing source governance metadata.")

    source_statuses = {_field(chunk, "source_status") for chunk in retrieved_chunks}
    if source_statuses == {"placeholder_educational"}:
        warnings.append("Retrieved context is placeholder educational material only.")

    if any(_field(chunk, "review_status") == "draft" for chunk in retrieved_chunks):
        warnings.append("Retrieved context includes draft KB profiles.")

    if any(
        _field(chunk, "clinical_validation_status") in {"", "not_validated", "engineering_only"}
        for chunk in retrieved_chunks
    ):
        warnings.append("Retrieved context is not clinically validated.")

    if any(_bool_field(chunk, "patient_facing_allowed") for chunk in retrieved_chunks):
        warnings.append("Patient-facing output permission must be independently verified.")
    else:
        warnings.append("Patient-facing output is disabled for retrieved KB context.")

    return _dedupe(warnings)


def _field(chunk: Any, field_name: str) -> str:
    value = getattr(chunk, field_name, None)
    if value is None and isinstance(chunk, dict):
        value = chunk.get(field_name)
    return str(value).strip() if value is not None else ""


def _float_field(chunk: Any, field_name: str) -> float:
    try:
        return float(_field(chunk, field_name))
    except ValueError:
        return 0.0


def _bool_field(chunk: Any, field_name: str) -> bool:
    value = getattr(chunk, field_name, None)
    if value is None and isinstance(chunk, dict):
        value = chunk.get(field_name)
    return bool(value)


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
