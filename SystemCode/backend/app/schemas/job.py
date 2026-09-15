from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    job_id: str
    title: str
    company: str
    description: str = Field(..., min_length=1)
    location: str | None = None
    degree_required: str | None = None
    min_experience_years: float | None = None


class JobAnalysis(BaseModel):
    job_id: str
    title: str
    company: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    summary: str
