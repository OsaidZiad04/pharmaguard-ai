from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.ocr_service import list_available_ocr_providers  # noqa: E402


def build_provider_report_lines() -> list[str]:
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
        safety_status = "allowed" if allowed else "blocked"
        lines.extend(
            [
                f"- provider_name: {provider.provider_name}",
                f"  is_external_provider: {provider.is_external_provider}",
                f"  stores_images: {provider.stores_images}",
                f"  requires_network: {provider.requires_network}",
                f"  supported_content_types: {sorted(provider.supported_content_types)}",
                f"  safety_status: {safety_status}",
                f"  allowed_in_current_prototype_mode: {allowed}",
            ]
        )

    return lines


def main() -> int:
    for line in build_provider_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
