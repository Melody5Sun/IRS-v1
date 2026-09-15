from pydantic import BaseModel, Field

from app.schemas.job import JobAnalysisRequest
from app.schemas.resume import ResumeProfile


class RecommendationRequest(BaseModel):
    candidate: ResumeProfile
    jobs: list[JobAnalysisRequest] = Field(..., min_length=1)


class RecommendationItem(BaseModel):
    job_id: str
    title: str
    company: str
    score: float = Field(..., ge=0, le=1)
    eligible: bool
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
