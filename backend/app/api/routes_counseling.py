from fastapi import APIRouter

from app.schemas.counseling import CounselingRequest, CounselingResponse
from app.services.counseling_service import generate_counseling_note

router = APIRouter(prefix="/counseling", tags=["counseling"])


@router.post("/generate", response_model=CounselingResponse)
def generate_counseling(payload: CounselingRequest) -> CounselingResponse:
    return generate_counseling_note(payload)
