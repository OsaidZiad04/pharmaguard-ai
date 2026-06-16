from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


DEMO_CASES_PATH = REPO_ROOT / "data" / "evaluation" / "final_demo_cases.json"


def load_final_demo_cases(path: Path = DEMO_CASES_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_final_demo_report_lines(cases: list[dict[str, Any]] | None = None) -> list[str]:
    cases = cases or load_final_demo_cases()
    lines = [
        "PharmaGuard AI Final Demo Report",
        "Demo planning only; synthetic scenarios are not clinical validation.",
        "Core message: pharmacist-centered, safety-first, evaluation-driven prototype.",
        f"total demo cases: {len(cases)}",
        "",
    ]

    for case in cases:
        lines.extend(
            [
                f"## {case['case_id']} - {case['title']}",
                f"scenario_type: {case['scenario_type']}",
                f"fixture_reference: {case.get('fixture_reference') or 'none'}",
                f"expected_medications: {case['expected_medications']}",
                f"expected_safety_findings: {case['expected_safety_findings']}",
                f"expected_retrieval_behavior: {case['expected_retrieval_behavior']}",
                f"expected_pharmacist_action: {case['expected_pharmacist_action']}",
                "demo_talking_points:",
            ]
        )
        lines.extend([f"- {point}" for point in case["demo_talking_points"]])
        lines.extend(
            [
                "limitations:",
                "- Draft placeholder KB only; not clinically validated.",
                "- Pharmacist review remains mandatory.",
                "- Patient-facing output remains disabled.",
                "",
            ]
        )

    return lines


def main() -> int:
    cases = load_final_demo_cases()
    for line in build_final_demo_report_lines(cases):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
