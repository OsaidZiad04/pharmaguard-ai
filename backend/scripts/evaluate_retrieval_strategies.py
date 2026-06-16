from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.retrieval_evaluation import evaluate_retrieval_strategies  # noqa: E402


def build_report_lines() -> list[str]:
    report = evaluate_retrieval_strategies()
    lines = [
        "PharmaGuard AI Retrieval Strategy Evaluation",
        "warning: retrieval metrics are engineering checks, not clinical validation.",
        f"total cases: {report['total_cases']}",
        f"recommended default strategy: {report['recommended_default_strategy']}",
        f"overall status: {'PASS' if report['passed'] else 'REVIEW'}",
        "strategy summary:",
    ]

    for strategy in report["strategies"]:
        lines.extend(
            [
                f"- {strategy['strategy_name']}: {'PASS' if strategy['passed'] else 'REVIEW'}",
                f"  top_k_hit_rate: {strategy['top_k_hit_rate']}",
                f"  expected_source_hit_rate: {strategy['expected_source_hit_rate']}",
                f"  expected_section_hit_rate: {strategy['expected_section_hit_rate']}",
                f"  insufficient_context_correctness: {strategy['insufficient_context_correctness']}",
                f"  governance_metadata_presence: {strategy['governance_metadata_presence']}",
                f"  weak_retrieval_detection: {strategy['weak_retrieval_detection']}",
                f"  average_retrieved_chunks: {strategy['average_retrieved_chunks']}",
            ]
        )

    if report["warnings"]:
        lines.append("warnings:")
        lines.extend([f"- {warning}" for warning in report["warnings"]])

    return lines


def main() -> int:
    for line in build_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
