from collections import Counter
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ocr.provider_candidates import (  # noqa: E402
    candidate_allowed_in_prototype,
    list_provider_candidates,
    summarize_candidate_readiness,
)
from app.ocr.activation_policy import evaluate_ocr_provider_activation  # noqa: E402
from app.ocr.ocr_config import get_ocr_runtime_config  # noqa: E402
from app.ocr.provider_dependencies import get_provider_dependency_status  # noqa: E402
from app.ocr.provider_swap_readiness import assess_provider_swap_readiness  # noqa: E402


def build_candidate_report_lines() -> list[str]:
    config = get_ocr_runtime_config()
    candidates = list_provider_candidates()
    status_counts = Counter(candidate.current_status for candidate in candidates)
    prototype_allowed = [
        candidate for candidate in candidates if candidate_allowed_in_prototype(candidate)
    ]
    requiring_network = [candidate for candidate in candidates if candidate.requires_network]
    storing_images = [candidate for candidate in candidates if candidate.stores_images]
    system_dependencies = [
        candidate for candidate in candidates if candidate.requires_system_dependency
    ]

    lines = [
        "PharmaGuard AI OCR Candidate Report",
        "Candidate comparison is metadata-only and is not clinical validation.",
        "No planned OCR engine is executed or called by this report.",
        f"total candidates: {len(candidates)}",
        f"implemented candidates: {status_counts.get('implemented', 0)}",
        f"planned candidates: {status_counts.get('planned', 0)}",
        f"disallowed candidates: {status_counts.get('disallowed_for_prototype', 0)}",
        f"prototype_allowed candidates: {len(prototype_allowed)}",
        f"candidates requiring network: {len(requiring_network)}",
        f"candidates requiring image storage: {len(storing_images)}",
        f"candidates requiring system dependencies: {len(system_dependencies)}",
        "per-candidate readiness:",
    ]

    for candidate in candidates:
        summary = summarize_candidate_readiness(candidate)
        readiness = assess_provider_swap_readiness(candidate)
        dependency_status = get_provider_dependency_status(candidate.provider_id)
        activation_results = {
            mode: evaluate_ocr_provider_activation(
                provider_id=candidate.provider_id,
                mode=mode,
                config=config,
            )
            for mode in [
                "default_workflow",
                "benchmark",
                "prototype_explicit",
                "production",
            ]
        }
        lines.extend(
            [
                f"- provider_id: {candidate.provider_id}",
                f"  display_name: {candidate.display_name}",
                f"  provider_type: {candidate.provider_type}",
                f"  current_status: {candidate.current_status}",
                f"  adapter_defined: {summary['adapter_defined']}",
                f"  active_in_prototype: {summary['active_in_prototype']}",
                f"  default_provider: {summary['default_provider']}",
                f"  benchmark_available: {summary['benchmark_available']}",
                f"  prototype_allowed: {summary['prototype_allowed']}",
                f"  production_possible_after_review: {candidate.production_possible_after_review}",
                f"  expected_privacy_risk: {candidate.expected_privacy_risk}",
                f"  dependency_available: {dependency_status.available}",
                f"  dependency_details: {dependency_status.details}",
                f"  readiness_summary: {summary['readiness_summary']}",
                f"  ready_for_prototype: {readiness.ready_for_prototype}",
                f"  ready_for_future_evaluation: {readiness.ready_for_future_evaluation}",
                f"  allowed_for_default_workflow: {activation_results['default_workflow'].allowed}",
                f"  allowed_for_benchmark: {activation_results['benchmark'].allowed}",
                f"  allowed_for_prototype_explicit: {activation_results['prototype_explicit'].allowed}",
                f"  allowed_for_production: {activation_results['production'].allowed}",
                f"  correction_gate_required: {activation_results['default_workflow'].correction_gate_required}",
                "  activation_blocking_reasons: "
                f"{ {mode: result.blocking_reasons for mode, result in activation_results.items()} }",
                f"  blocking_reasons: {readiness.blocking_reasons}",
                f"  warnings: {readiness.warnings}",
                f"  required_next_steps: {readiness.required_next_steps}",
            ]
        )

    return lines


def main() -> int:
    for line in build_candidate_report_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
