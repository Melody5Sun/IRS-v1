from fastapi import APIRouter

from app.schemas.resume import ResumeDocument, ResumeParseRequest
from app.services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()


@router.post("/parse", response_model=ResumeDocument)
def parse_resume(request: ResumeParseRequest) -> ResumeDocument:
    return resume_service.parse_text(request.text)
