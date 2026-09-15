from fastapi import APIRouter

from app.schemas.resume import ResumeParseRequest, ResumeProfile
from app.services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()


@router.post("/parse", response_model=ResumeProfile)
def parse_resume(request: ResumeParseRequest) -> ResumeProfile:
    return resume_service.parse_text(request.text)
