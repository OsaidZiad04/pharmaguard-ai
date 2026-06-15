from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.rag.evaluation import run_rag_evaluation


def main() -> int:
    report = run_rag_evaluation()

    print("PharmaGuard AI RAG Evaluation")
    print(f"total cases: {report['total_cases']}")
    print(f"passed cases: {report['passed_cases']}")
    print(f"failed cases: {report['failed_cases']}")
    print()

    print("Per-case status:")
    for case in report["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(
            f"- {status} {case['case_id']} | retrieved={case['retrieved_count']} "
            f"| insufficient={case['insufficient_context']}"
        )
        if not case["passed"]:
            failed_retrieval = [
                name for name, passed in case["retrieval_checks"].items() if not passed
            ]
            failed_generation = [
                name for name, passed in case["generation_checks"].items() if not passed
            ]
            print(f"  retrieval failures: {', '.join(failed_retrieval) or 'none'}")
            print(f"  generation failures: {', '.join(failed_generation) or 'none'}")

    print()
    print("Retrieval summary:")
    for key, value in sorted(report["retrieval_summary"].items()):
        print(f"- {key}: {value}")

    print()
    print("Generation safety summary:")
    for key, value in sorted(report["generation_safety_summary"].items()):
        print(f"- {key}: {value}")

    return 0 if report["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
