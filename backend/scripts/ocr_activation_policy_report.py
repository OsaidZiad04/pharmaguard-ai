from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ocr.activation_policy import evaluate_ocr_provider_activation  # noqa: E402
from app.ocr.ocr_config import get_ocr_runtime_config  # noqa: E402
from app.ocr.provider_dependencies import (  # noqa: E402
    MOCK_PROVIDER_ID,
    SYNTHETIC_FIXTURE_PROVIDER_ID,
    TESSERACT_PROVIDER_ID,
)


PROVIDER_IDS = [
    MOCK_PROVIDER_ID,
    SYNTHETIC_FIXTURE_PROVIDER_ID,
    TESSERACT_PROVIDER_ID,
    "cloud_ocr_candidate_placeholder",
]
MODES = ["default_workflow", "benchmark", "prototype_explicit", "production"]


def build_activation_policy_report_lines() -> list[str]:
    config = get_ocr_runtime_config()
    lines = [
        "PharmaGuard AI OCR Activation Policy Report",
        "Policy report is engineering governance only; it is not clinical validation.",
        f"default_provider: {config.default_provider}",
        f"ocr_mode: {config.ocr_mode}",
        f"enable_tesseract_prototype: {config.enable_tesseract_prototype}",
        f"allow_external_ocr: {config.allow_external_ocr}",
        f"tesseract_benchmark_passed: {config.tesseract_benchmark_passed}",
        f"config_warnings: {config.warnings}",
        "provider policies:",
    ]

    for provider_id in PROVIDER_IDS:
        lines.append(f"- provider_id: {provider_id}")
        for mode in MODES:
            result = evaluate_ocr_provider_activation(
                provider_id=provider_id,
                mode=mode,
                config=config,
            )
            lines.extend(
                [
                    f"  mode: {mode}",
                    f"    allowed: {result.allowed}",
                    f"    correction_gate_required: {result.correction_gate_required}",
                    f"    default_provider: {result.default_provider}",
                    f"    production_allowed: {result.production_allowed}",
                    f"    blocking_reasons: {result.blocking_reasons}",
                    f"    warnings: {result.warnings}",
                ]
            )

    return lines


def main() -> int:
    for line in build_activation_policy_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
