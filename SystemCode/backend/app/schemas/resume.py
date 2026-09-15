from pydantic import BaseModel, Field


class ResumeParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Plain text extracted from a resume.")


class ResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    work_authorization: str | None = None
