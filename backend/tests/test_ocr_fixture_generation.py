from pathlib import Path
import subprocess
import sys

import pytest

from app.ocr.fixture_inspection import inspect_ocr_fixture, inspect_required_ocr_fixtures


pytest.importorskip("PIL")


def test_generate_ocr_fixtures_creates_readable_non_blank_pngs() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/generate_ocr_fixtures.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "synthetic_paracetamol_clean.png" in result.stdout

    inspection_results = inspect_required_ocr_fixtures()
    assert len(inspection_results) >= 6
    for inspection in inspection_results:
        assert inspection.exists is True
        assert inspection.width is not None and inspection.width > 12
        assert inspection.height is not None and inspection.height > 12
        assert inspection.unique_pixel_count is not None
        assert inspection.unique_pixel_count > 10
        assert inspection.likely_blank is False
        assert inspection.ocr_readable_candidate is True


def test_fixture_inspection_flags_blank_small_images() -> None:
    from PIL import Image

    blank_path = Path(__file__).resolve().parents[1] / ".test_blank_fixture.png"
    try:
        Image.new("RGB", (12, 12), "white").save(blank_path)
        inspection = inspect_ocr_fixture(blank_path)
    finally:
        blank_path.unlink(missing_ok=True)

    assert inspection.exists is True
    assert inspection.width == 12
    assert inspection.height == 12
    assert inspection.likely_blank is True
    assert inspection.ocr_readable_candidate is False
    assert "image_too_small_for_ocr_benchmark" in inspection.issues
