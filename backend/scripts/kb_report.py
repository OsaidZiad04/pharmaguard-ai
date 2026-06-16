from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.kb.governance import validate_governance_metadata  # noqa: E402
from app.kb.validator import build_coverage_report  # noqa: E402


def build_report_lines() -> list[str]:
    report = build_coverage_report()
    validation = report.validation_report
    blocking_issues = [issue for issue in validation.issues if issue.severity == "error"]
    governance_report = validate_governance_metadata()

    lines = [
        "PharmaGuard AI Knowledge Base Report",
        "Current content is educational placeholder material, not clinical validation.",
        f"Total profiles: {report.total_profiles}",
        f"Total enabled profiles: {report.total_enabled_profiles}",
        f"Total aliases: {report.total_aliases}",
        f"Profiles by review_status: {report.profiles_by_review_status}",
        f"Profiles by source_status: {report.profiles_by_source_status}",
        f"Validation status: {'PASS' if validation.valid else 'FAIL'}",
        f"Validation issues: {len(validation.issues)}",
        f"Blocking validation issues: {len(blocking_issues)}",
        f"Missing sections: {validation.missing_required_sections}",
        f"Alias conflicts: {validation.alias_conflicts}",
        f"Disabled profiles: {validation.disabled_profiles}",
        f"Unreviewed draft profiles: {validation.unreviewed_profiles}",
        "Governance summary:",
        f"- Profiles by clinical_validation_status: {governance_report.profiles_by_clinical_validation_status}",
        f"- Patient-facing allowed profiles: {governance_report.patient_facing_allowed_count}",
        f"- Pharmacist review required profiles: {governance_report.pharmacist_review_required_count}",
        f"- Governance blocking issues: {len(governance_report.blocking_issues)}",
        f"- Governance warnings: {len(governance_report.warnings)}",
    ]

    if validation.issues:
        lines.append("Issue details:")
        for issue in validation.issues:
            location = issue.drug_id or issue.profile_file or "registry"
            lines.append(f"- [{issue.severity}] {issue.code} ({location}): {issue.message}")

    return lines


def main() -> int:
    for line in build_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
