from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ocr.fixture_inspection import inspect_required_ocr_fixtures  # noqa: E402


def main() -> int:
    try:
        results = inspect_required_ocr_fixtures()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    print("PharmaGuard AI OCR Fixture Inspection")
    print("Synthetic fixtures only; no real prescription images are inspected.")
    all_ready = True
    for result in results:
        all_ready = all_ready and result.ocr_readable_candidate
        print(
            f"- filename: {result.filename} | "
            f"exists: {result.exists} | "
            f"size: {result.width}x{result.height} | "
            f"min_pixel: {result.min_pixel_value} | "
            f"max_pixel: {result.max_pixel_value} | "
            f"contrast: {result.contrast_range} | "
            f"unique_pixels: {result.unique_pixel_count} | "
            f"likely_blank: {result.likely_blank} | "
            f"ocr_readable_candidate: {result.ocr_readable_candidate} | "
            f"issues: {result.issues}"
        )

    print(f"inspection_status: {'PASS' if all_ready else 'FAIL'}")
    return 0 if all_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
