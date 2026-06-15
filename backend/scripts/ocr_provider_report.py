from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.ocr_service import list_available_ocr_providers  # noqa: E402
from app.ocr.evaluation import run_ocr_evaluation  # noqa: E402


def build_provider_report_lines() -> list[str]:
    evaluation_report = run_ocr_evaluation()
    gate_results = {
        result["provider_name"]: result
        for result in evaluation_report["quality_gate_summary"]["results"]
    }
    lines = [
        "PharmaGuard AI OCR Provider Report",
        "Current prototype mode permits only local, non-networked, non-storing providers.",
    ]

    for provider in list_available_ocr_providers():
        allowed = (
            not provider.is_external_provider
            and not provider.stores_images
            and not provider.requires_network
        )
        gate_result = gate_results.get(provider.provider_name, {})
        quality_gate_eligible = bool(gate_result.get("passed", False))
        prototype_allowed = allowed and quality_gate_eligible
        safety_status = "allowed" if allowed else "blocked"
        lines.extend(
            [
                f"- provider_name: {provider.provider_name}",
                f"  is_external_provider: {provider.is_external_provider}",
                f"  stores_images: {provider.stores_images}",
                f"  requires_network: {provider.requires_network}",
                f"  can_be_used_without_network: {not provider.requires_network}",
                f"  supported_content_types: {sorted(provider.supported_content_types)}",
                f"  safety_status: {safety_status}",
                f"  quality_gate_eligible: {quality_gate_eligible}",
                f"  failed_quality_checks: {gate_result.get('failed_checks', [])}",
                f"  quality_gate_warnings: {gate_result.get('warnings', [])}",
                f"  allowed_in_current_prototype_mode: {prototype_allowed}",
            ]
        )

    return lines


def main() -> int:
    for line in build_provider_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
