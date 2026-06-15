from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.ocr_service import list_available_ocr_providers  # noqa: E402
from app.services.ocr_service import list_known_ocr_provider_adapters  # noqa: E402
from app.ocr.evaluation import run_ocr_evaluation  # noqa: E402
from app.ocr.provider_dependencies import get_provider_dependency_status  # noqa: E402


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

    active_provider_names = {
        provider.provider_name for provider in list_available_ocr_providers()
    }

    for provider in list_known_ocr_provider_adapters():
        active_in_prototype = provider.provider_name in active_provider_names
        dependency_status = get_provider_dependency_status(provider.provider_name)
        allowed = (
            not provider.is_external_provider
            and not provider.stores_images
            and not provider.requires_network
            and getattr(provider, "enabled_by_default", True)
            and getattr(provider, "prototype_allowed", True)
            and (
                not getattr(provider, "requires_system_dependency", False)
                or dependency_status.available
            )
        )
        gate_result = gate_results.get(provider.provider_name, {})
        quality_gate_eligible = bool(gate_result.get("passed", False))
        prototype_allowed = active_in_prototype and allowed and quality_gate_eligible
        safety_status = "allowed" if allowed else "blocked"
        lines.extend(
            [
                f"- provider_name: {provider.provider_name}",
                f"  active_in_prototype: {active_in_prototype}",
                f"  is_external_provider: {provider.is_external_provider}",
                f"  stores_images: {provider.stores_images}",
                f"  requires_network: {provider.requires_network}",
                f"  requires_system_dependency: {getattr(provider, 'requires_system_dependency', False)}",
                f"  enabled_by_default: {getattr(provider, 'enabled_by_default', True)}",
                f"  dependency_available: {dependency_status.available}",
                f"  dependency_details: {dependency_status.details}",
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
