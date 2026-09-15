from fastapi import APIRouter

from app.schemas.job import JobAnalysis, JobAnalysisRequest
from app.services.job_service import JobService

router = APIRouter()
job_service = JobService()


@router.post("/analyze", response_model=JobAnalysis)
def analyze_job(request: JobAnalysisRequest) -> JobAnalysis:
    return job_service.analyze(request)
