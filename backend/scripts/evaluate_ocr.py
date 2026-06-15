from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ocr.evaluation import run_ocr_evaluation  # noqa: E402


def main() -> int:
    report = run_ocr_evaluation()

    print("PharmaGuard AI OCR Evaluation")
    print(f"total cases: {report['total_cases']}")
    print(f"text-only cases: {report['text_only_cases']}")
    print(f"fixture-backed cases: {report['fixture_backed_cases']}")
    print(f"provider used: {report['provider_used']}")
    print(f"passed cases: {report['passed_cases']}")
    print(f"failed cases: {report['failed_cases']}")
    print(f"average character error rate: {report['average_character_error_rate']}")
    print(f"average word error rate: {report['average_word_error_rate']}")
    print("warning: OCR benchmark metrics are engineering checks, not clinical validation.")
    print("medication detection summary:")
    print(f"- passed: {report['medication_detection_summary']['passed']}")
    print(f"- failed: {report['medication_detection_summary']['failed']}")
    print("privacy warning summary:")
    print(f"- passed: {report['privacy_warning_summary']['passed']}")
    print(f"- failed: {report['privacy_warning_summary']['failed']}")
    print("provider-level summary:")
    for provider_name, summary in report["provider_summaries"].items():
        print(
            f"- {provider_name}: cases={summary['total_cases']} "
            f"passed={summary['passed_cases']} failed={summary['failed_cases']} "
            f"avg_cer={summary['average_character_error_rate']} "
            f"avg_wer={summary['average_word_error_rate']}"
        )
    print("quality gate summary:")
    print(f"- passed providers: {report['quality_gate_summary']['passed']}")
    print(f"- failed providers: {report['quality_gate_summary']['failed']}")
    for gate_result in report["quality_gate_summary"]["results"]:
        status = "PASS" if gate_result["passed"] else "FAIL"
        print(
            f"- {status} {gate_result['provider_name']} | "
            f"failed_checks={gate_result['failed_checks']} | "
            f"warnings={gate_result['warnings']}"
        )
    print("per-case status:")
    for result in report["case_results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"- {status} {result['case_id']} | "
            f"cer={result['character_error_rate']} | "
            f"wer={result['word_error_rate']} | "
            f"medication_hit={result['medication_detection_hit']} | "
            f"privacy_match={result['privacy_warning_match']}"
        )

    quality_gates_failed = report["quality_gate_summary"]["failed"] > 0
    return 0 if report["failed_cases"] == 0 and not quality_gates_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
