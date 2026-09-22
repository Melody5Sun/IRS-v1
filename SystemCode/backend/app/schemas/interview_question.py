from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import DifficultyLevel


class InterviewQuestion(BaseModel):
    id: int | None = None
    source: str
    external_id: str
    question_text: str
    standard_answer: str = ""
    difficulty_level: DifficultyLevel = "not_stated"
    company: str | None = None
    published_at: datetime | None = None
    collected_at: datetime
    question_embedding: list[float] | None = None
    skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
