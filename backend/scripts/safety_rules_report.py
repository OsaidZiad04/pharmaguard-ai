from collections import Counter
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.retriever import retrieve_contexts  # noqa: E402
from app.safety.medication_rules import analyze_medication_safety_rules  # noqa: E402
from app.services.extraction_service import extract_medication_candidates  # noqa: E402


SCENARIOS = [
    {
        "scenario_id": "SAFE-RULE-001",
        "text": "Medication: Paracetamol 500 mg. Directions: Take every 8 hours for 3 days.",
        "expected_rules": {"not_clinically_validated", "patient_facing_not_allowed"},
    },
    {
        "scenario_id": "SAFE-RULE-002",
        "text": "Medication: Ibuprofen. Directions: Take every 8 hours for 2 days.",
        "expected_rules": {"missing_dose"},
    },
    {
        "scenario_id": "SAFE-RULE-003",
        "text": "Medication: Amoxicillin 500 mg. Directions: Take as directed for 5 days.",
        "expected_rules": {"missing_frequency"},
    },
    {
        "scenario_id": "SAFE-RULE-004",
        "text": "Medication: Cetirizine 10 mg. Directions: Take daily.",
        "expected_rules": {"missing_duration"},
    },
    {
        "scenario_id": "SAFE-RULE-005",
        "text": "Medication: Salbutamol 100 mcg. Directions: Use every 6 hours.",
        "expected_rules": {"missing_route"},
    },
    {
        "scenario_id": "SAFE-RULE-006",
        "text": "Medication: Paracetamol 500 mg. Medication: Cetirizine 10 mg. Directions: Take daily for 2 days.",
        "expected_rules": {"multiple_medications_detected"},
    },
    {
        "scenario_id": "SAFE-RULE-007",
        "text": "Medication: Xyzmed 20 mg. Directions: Take daily for 2 days.",
        "expected_rules": {"unsupported_medication_detected"},
    },
    {
        "scenario_id": "SAFE-RULE-008",
        "text": "Synthetic note only. No medication listed.",
        "expected_rules": {"no_medication_detected"},
    },
    {
        "scenario_id": "SAFE-RULE-009",
        "text": "Patient: SYNTHETIC ONLY. Medication: Metformin 500 mg. Directions: Take daily for 7 days.",
        "expected_rules": {"possible_identifier_detected"},
    },
    {
        "scenario_id": "SAFE-RULE-010",
        "text": "Medication: Omeprazole 20. Directions: Take daily for 5 days.",
        "expected_rules": {"ambiguous_strength_or_units"},
    },
]


def run_safety_rules_report() -> dict:
    case_reports = [_run_scenario(scenario) for scenario in SCENARIOS]
    passed_cases = [case for case in case_reports if case["passed"]]
    failed_cases = [case for case in case_reports if not case["passed"]]
    rule_counter = Counter(
        rule_id for case in case_reports for rule_id in case["triggered_rules"]
    )
    severity_counter = Counter(
        severity for case in case_reports for severity in case["severity_counts"].elements()
    )

    return {
        "total_scenarios": len(case_reports),
        "passed_scenarios": len(passed_cases),
        "failed_scenarios": len(failed_cases),
        "cases": case_reports,
        "rules_triggered": dict(sorted(rule_counter.items())),
        "severity_summary": dict(sorted(severity_counter.items())),
        "pharmacist_review_required_count": sum(
            1 for case in case_reports if case["pharmacist_review_required"]
        ),
        "patient_facing_blocked_count": sum(
            1 for case in case_reports if not case["patient_facing_allowed"]
        ),
    }


def build_report_lines() -> list[str]:
    report = run_safety_rules_report()
    lines = [
        "PharmaGuard AI Medication Safety Rules Report",
        "warning: deterministic engineering safety support only; not clinical validation.",
        f"total scenarios: {report['total_scenarios']}",
        f"passed scenarios: {report['passed_scenarios']}",
        f"failed scenarios: {report['failed_scenarios']}",
        f"rules triggered: {report['rules_triggered']}",
        f"severity summary: {report['severity_summary']}",
        f"pharmacist review required count: {report['pharmacist_review_required_count']}",
        f"patient-facing blocked count: {report['patient_facing_blocked_count']}",
        "per-scenario status:",
    ]
    for case in report["cases"]:
        lines.append(
            f"- {'PASS' if case['passed'] else 'FAIL'} {case['scenario_id']} "
            f"| rules={case['triggered_rules']} | missing={case['missing_expected_rules']}"
        )
    return lines


def main() -> int:
    report = run_safety_rules_report()
    for line in build_report_lines():
        print(line)
    return 0 if report["failed_scenarios"] == 0 else 1


def _run_scenario(scenario: dict) -> dict:
    extracted = extract_medication_candidates(scenario["text"])
    retrieved_chunks = []
    for medication in extracted:
        retrieved_chunks.extend(
            retrieve_contexts(
                query=f"{medication['name']} counseling safety",
                medication_name=medication["name"],
                top_k=3,
            )
        )
    analysis = analyze_medication_safety_rules(
        prescription_text=scenario["text"],
        extracted_medications=extracted,
        retrieved_chunks=retrieved_chunks,
    )
    triggered_rules = sorted({finding.rule_id for finding in analysis.findings})
    missing_expected = sorted(set(scenario["expected_rules"]) - set(triggered_rules))
    severity_counts = Counter(finding.severity for finding in analysis.findings)

    return {
        "scenario_id": scenario["scenario_id"],
        "passed": not missing_expected,
        "triggered_rules": triggered_rules,
        "missing_expected_rules": missing_expected,
        "severity_counts": severity_counts,
        "pharmacist_review_required": analysis.pharmacist_review_required,
        "patient_facing_allowed": analysis.patient_facing_allowed,
    }


if __name__ == "__main__":
    raise SystemExit(main())
