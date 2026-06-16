from __future__ import annotations

from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
FIXTURE_DIR = REPO_ROOT / "data" / "evaluation" / "ocr_fixtures"


FIXTURE_DEFINITIONS = [
    {
        "filename": "synthetic_paracetamol_clean.png",
        "label": "clean paracetamol synthetic prescription",
        "size": (1200, 720),
        "lines": [
            "SYNTHETIC PRESCRIPTION - NOT REAL",
            "Medication: Paracetamol 500 mg",
            "Directions: Take 1 tablet every 8 hours as needed",
            "Pharmacist review required",
        ],
        "noise": False,
    },
    {
        "filename": "synthetic_ibuprofen_noisy.png",
        "label": "readable noisy ibuprofen synthetic prescription",
        "size": (1200, 720),
        "lines": [
            "SYNTHETIC PRESCRIPTION - NOT REAL",
            "Medication: Ibuprofen 200 mg",
            "Directions: Take with food as directed",
            "Pharmacist review required",
        ],
        "noise": True,
    },
    {
        "filename": "synthetic_amoxicillin_possible_identifier.png",
        "label": "amoxicillin synthetic prescription with fake identifier-like labels",
        "size": (1200, 760),
        "lines": [
            "SYNTHETIC PRESCRIPTION - NOT REAL",
            "Medication: Amoxicillin 500 mg",
            "Directions: Take as directed",
            "Fake Patient Code: SYN-000123",
            "Fake Phone: 000-000-0000",
            "Pharmacist review required",
        ],
        "noise": False,
    },
    {
        "filename": "synthetic_no_medication.png",
        "label": "synthetic note without medication",
        "size": (1200, 620),
        "lines": [
            "SYNTHETIC NOTE - NOT REAL",
            "No medication listed",
            "Pharmacist review required",
        ],
        "noise": False,
    },
    {
        "filename": "synthetic_metformin_clean.png",
        "label": "clean metformin synthetic prescription",
        "size": (1200, 720),
        "lines": [
            "SYNTHETIC PRESCRIPTION - NOT REAL",
            "Medication: Metformin 500 mg",
            "Directions: Take with meals as directed",
            "Pharmacist review required",
        ],
        "noise": False,
    },
    {
        "filename": "synthetic_multiple_meds.png",
        "label": "synthetic prescription with multiple supported medications",
        "size": (1200, 760),
        "lines": [
            "SYNTHETIC PRESCRIPTION - NOT REAL",
            "Medication: Paracetamol 500 mg",
            "Medication: Cetirizine 10 mg",
            "Directions: Review each medication separately",
            "Pharmacist review required",
        ],
        "noise": False,
    },
]


def main() -> int:
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
    except ImportError:
        print(
            "Pillow is required to generate OCR fixtures. "
            "Install Pillow in the local development environment and rerun this script.",
            file=sys.stderr,
        )
        return 1

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for fixture in FIXTURE_DEFINITIONS:
        output_path = FIXTURE_DIR / fixture["filename"]
        image = _create_fixture_image(
            Image=Image,
            ImageDraw=ImageDraw,
            ImageFilter=ImageFilter,
            ImageFont=ImageFont,
            size=fixture["size"],
            lines=fixture["lines"],
            add_noise=fixture["noise"],
        )
        image.save(output_path, format="PNG")
        print(
            f"generated: {output_path} | size={fixture['size'][0]}x{fixture['size'][1]} "
            f"| label={fixture['label']}"
        )
    return 0


def _create_fixture_image(
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont,
    size: tuple[int, int],
    lines: list[str],
    add_noise: bool,
):
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)

    title_font = _load_font(ImageFont, 46)
    body_font = _load_font(ImageFont, 42)
    small_font = _load_font(ImageFont, 28)

    draw.rectangle((38, 38, size[0] - 38, size[1] - 38), outline=(80, 120, 120), width=3)
    y = 86
    for index, line in enumerate(lines):
        font = title_font if index == 0 else body_font
        fill = (20, 50, 50) if index == 0 else (25, 25, 25)
        draw.text((82, y), line, fill=fill, font=font)
        y += 82 if index == 0 else 76

    draw.text(
        (82, size[1] - 76),
        "Synthetic OCR benchmark fixture only",
        fill=(85, 85, 85),
        font=small_font,
    )

    if add_noise:
        _add_deterministic_noise(draw, size)
        image = image.filter(ImageFilter.GaussianBlur(radius=0.35))

    return image


def _load_font(ImageFont, size: int):
    font_candidates = [
        "DejaVuSans.ttf",
        "Arial.ttf",
        "LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _add_deterministic_noise(draw, size: tuple[int, int]) -> None:
    width, height = size
    for index in range(0, 220):
        x = (index * 47) % width
        y = (index * 89) % height
        shade = 205 + (index % 35)
        draw.point((x, y), fill=(shade, shade, shade))
    for index in range(0, 18):
        y = 96 + index * 31
        draw.line((70, y, width - 70, y + (index % 3) - 1), fill=(232, 232, 232), width=1)


if __name__ == "__main__":
    raise SystemExit(main())
