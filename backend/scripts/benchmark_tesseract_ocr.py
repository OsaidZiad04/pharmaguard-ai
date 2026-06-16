from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ocr.tesseract_benchmark import run_tesseract_benchmark  # noqa: E402


def main() -> int:
    report = run_tesseract_benchmark()

    print("PharmaGuard AI Local Tesseract OCR Benchmark")
    print("warning: synthetic engineering benchmark only; not clinical validation.")
    print("warning: Tesseract remains disabled by default and is not the default provider.")
    print(f"provider: {report['provider_name']}")
    print(f"status: {report['status']}")
    print(f"dependency_available: {report['dependency_available']}")
    print(f"dependency_details: {report['dependency_details']}")
    if report["status"] == "skipped":
        print(report["message"])
    print(f"fixture count tested: {report['fixture_count_tested']}")
    print(
        "skipped descriptor-only fixtures: "
        f"{report['skipped_descriptor_only_fixtures']}"
    )
    print(f"skipped missing fixtures: {report['skipped_missing_fixtures']}")
    print(f"passed cases: {report['passed_cases']}")
    print(f"failed cases: {report['failed_cases']}")
    print(f"average character error rate: {report['average_character_error_rate']}")
    print(f"average word error rate: {report['average_word_error_rate']}")
    print(f"average token overlap: {report['average_token_overlap_score']}")
    print("medication detection summary:")
    print(f"- passed: {report['medication_detection_summary']['passed']}")
    print(f"- failed: {report['medication_detection_summary']['failed']}")
    print("privacy warning summary:")
    print(f"- passed: {report['privacy_warning_summary']['passed']}")
    print(f"- failed: {report['privacy_warning_summary']['failed']}")
    print(f"quality gate status: {report['quality_gate_status']}")
    if report["quality_gate_result"]:
        gate_result = report["quality_gate_result"]
        print(f"- failed checks: {gate_result['failed_checks']}")
        print(f"- warnings: {gate_result['warnings']}")
    print("per-case status:")
    for result in report["case_results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"- {status} {result['case_id']} | "
            f"fixture={result['fixture_filename']} | "
            f"cer={result['character_error_rate']} | "
            f"wer={result['word_error_rate']} | "
            f"overlap={result['token_overlap_score']} | "
            f"failed_checks={result['failed_checks']}"
        )
    if report["skipped_cases"]:
        print("skipped fixtures:")
        for skipped in report["skipped_cases"]:
            print(
                f"- {skipped['case_id']} | "
                f"fixture={skipped['fixture_filename']} | reason={skipped['reason']}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
