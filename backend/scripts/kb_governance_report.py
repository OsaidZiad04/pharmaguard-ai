from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.kb.governance import validate_governance_metadata  # noqa: E402


def build_report_lines() -> list[str]:
    report = validate_governance_metadata()

    lines = [
        "PharmaGuard AI Knowledge Base Governance Report",
        "Current drug content is draft educational placeholder material, not clinical validation.",
        f"Total profiles: {report.total_profiles}",
        f"Enabled for RAG: {report.enabled_for_rag_profiles}",
        f"Profiles by source_status: {report.profiles_by_source_status}",
        f"Profiles by review_status: {report.profiles_by_review_status}",
        f"Profiles by clinical_validation_status: {report.profiles_by_clinical_validation_status}",
        f"Patient-facing allowed profiles: {report.patient_facing_allowed_count}",
        f"Counseling draft allowed profiles: {report.counseling_draft_allowed_count}",
        f"Pharmacist review required profiles: {report.pharmacist_review_required_count}",
        f"Source catalog categories: {report.source_catalog_categories}",
        f"Governance status: {'PASS' if report.valid else 'FAIL'}",
        f"Blocking issues: {len(report.blocking_issues)}",
        f"Warnings: {len(report.warnings)}",
    ]

    if report.blocking_issues:
        lines.append("Blocking issue details:")
        for issue in report.blocking_issues:
            location = issue.drug_id or issue.profile_file or "registry"
            lines.append(f"- [{issue.code}] {location}: {issue.message}")

    if report.warnings:
        lines.append("Warning details:")
        for issue in report.warnings:
            location = issue.drug_id or issue.profile_file or "registry"
            lines.append(f"- [{issue.code}] {location}: {issue.message}")

    return lines


def main() -> int:
    for line in build_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
