from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.schemas.ocr import (
    OcrCorrectionRequest,
    OcrCorrectionResponse,
    OcrImageUploadResponse,
)
from app.services.ocr_audit_service import build_ocr_correction_audit
from app.services.ocr_service import (
    extract_text_from_image,
)


router = APIRouter(prefix="/ocr", tags=["ocr"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
SUPPORTED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@router.post("/extract-image", response_model=OcrImageUploadResponse)
async def extract_image(
    file: UploadFile = File(...),
    provider_name: str | None = Query(default=None),
    ocr_mode: str | None = Query(default=None),
) -> OcrImageUploadResponse:
    filename = file.filename or "uploaded_image"
    content_type = (file.content_type or "").lower()
    _validate_upload_type(filename, content_type)
    if (ocr_mode or "").strip().lower() == "benchmark":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benchmark OCR mode is only available through benchmark scripts.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Uploaded image is too large for Phase 2A OCR intake.",
        )

    try:
        extracted = extract_text_from_image(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
            provider_name=provider_name,
            ocr_mode=ocr_mode,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return OcrImageUploadResponse(
        filename=filename,
        content_type=content_type,
        extracted_text=extracted.extracted_text,
        confidence_score=extracted.confidence_score,
        provider_name=extracted.provider_name,
        is_external_provider=extracted.is_external_provider,
        stores_images=extracted.stores_images,
        requires_network=extracted.requires_network,
        supported_content_types=extracted.supported_content_types,
        unverified_ocr_output=True,
        pharmacist_review_required=True,
        privacy_warnings=extracted.privacy_warnings,
        detected_possible_identifiers=extracted.detected_possible_identifiers,
        correction_required=True,
        can_send_to_analysis=False,
    )


@router.post("/confirm-text", response_model=OcrCorrectionResponse)
def confirm_text(payload: OcrCorrectionRequest) -> OcrCorrectionResponse:
    corrected_text = payload.corrected_text.strip()
    audit = build_ocr_correction_audit(
        original_ocr_text=payload.extracted_text,
        corrected_text=corrected_text,
    )

    return OcrCorrectionResponse(
        corrected_text=corrected_text,
        pharmacist_review_required=True,
        correction_required=False,
        can_send_to_analysis=True,
        privacy_warnings=audit.privacy_warnings,
        detected_possible_identifiers=audit.detected_possible_identifiers,
        correction_audit=audit,
    )


def _validate_upload_type(filename: str, content_type: str) -> None:
    extension = Path(filename).suffix.lower()
    if content_type not in SUPPORTED_CONTENT_TYPES or extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported OCR upload type. Use PNG, JPG, JPEG, or WEBP images only.",
        )
