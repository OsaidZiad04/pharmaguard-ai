from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.ocr.evaluation import OCR_FIXTURES_DIR


REQUIRED_READABLE_FIXTURES = [
    "synthetic_paracetamol_clean.png",
    "synthetic_ibuprofen_noisy.png",
    "synthetic_amoxicillin_possible_identifier.png",
    "synthetic_no_medication.png",
    "synthetic_metformin_clean.png",
    "synthetic_multiple_meds.png",
]
MIN_READABLE_WIDTH = 1000
MIN_READABLE_HEIGHT = 500
MIN_CONTRAST_RANGE = 40
MIN_UNIQUE_PIXEL_COUNT = 10


@dataclass(frozen=True)
class OcrFixtureInspectionResult:
    filename: str
    exists: bool
    width: int | None
    height: int | None
    min_pixel_value: int | None
    max_pixel_value: int | None
    contrast_range: int | None
    unique_pixel_count: int | None
    likely_blank: bool
    ocr_readable_candidate: bool
    issues: list[str]

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


def inspect_required_ocr_fixtures(
    fixture_dir: Path = OCR_FIXTURES_DIR,
) -> list[OcrFixtureInspectionResult]:
    return [
        inspect_ocr_fixture(fixture_dir / fixture_filename)
        for fixture_filename in REQUIRED_READABLE_FIXTURES
    ]


def inspect_ocr_fixture(path: Path) -> OcrFixtureInspectionResult:
    if not path.exists():
        return OcrFixtureInspectionResult(
            filename=path.name,
            exists=False,
            width=None,
            height=None,
            min_pixel_value=None,
            max_pixel_value=None,
            contrast_range=None,
            unique_pixel_count=None,
            likely_blank=True,
            ocr_readable_candidate=False,
            issues=["missing_file"],
        )

    try:
        from PIL import Image
    except ImportError as error:
        raise RuntimeError(
            "Pillow is required to inspect OCR fixtures. Install Pillow locally and rerun."
        ) from error

    with Image.open(path) as image:
        grayscale = image.convert("L")
        width, height = grayscale.size
        pixel_data = getattr(grayscale, "get_flattened_data", grayscale.getdata)
        values = list(pixel_data())

    min_pixel = min(values) if values else None
    max_pixel = max(values) if values else None
    contrast_range = (
        max_pixel - min_pixel if min_pixel is not None and max_pixel is not None else None
    )
    unique_pixel_count = len(set(values))
    issues: list[str] = []

    if width < MIN_READABLE_WIDTH or height < MIN_READABLE_HEIGHT:
        issues.append("image_too_small_for_ocr_benchmark")
    if unique_pixel_count <= MIN_UNIQUE_PIXEL_COUNT:
        issues.append("low_pixel_variation")
    if contrast_range is not None and contrast_range < MIN_CONTRAST_RANGE:
        issues.append("low_contrast")

    likely_blank = (
        width <= 20
        or height <= 20
        or unique_pixel_count <= 2
        or (contrast_range is not None and contrast_range < 5)
    )
    if likely_blank and "likely_blank" not in issues:
        issues.append("likely_blank")

    return OcrFixtureInspectionResult(
        filename=path.name,
        exists=True,
        width=width,
        height=height,
        min_pixel_value=min_pixel,
        max_pixel_value=max_pixel,
        contrast_range=contrast_range,
        unique_pixel_count=unique_pixel_count,
        likely_blank=likely_blank,
        ocr_readable_candidate=not issues,
        issues=issues,
    )
