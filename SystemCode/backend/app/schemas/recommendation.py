from pydantic import BaseModel, Field

from app.schemas.job import JobAnalysisRequest
from app.schemas.resume import ResumeDocument


class RecommendationRequest(BaseModel):
    # 直接接收 /resumes/parse-pdf 的输出或 GET /profile 里的 resume，前端不需要做任何转换
    candidate: ResumeDocument
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
