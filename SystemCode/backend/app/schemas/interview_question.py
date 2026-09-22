from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import DifficultyLevel
from app.schemas.profile import TARGET_ROLES


_TARGET_ROLE_SET = frozenset(TARGET_ROLES)


class InterviewQuestion(BaseModel):
    id: int | None = None
    source: str
    external_id: str
    question_text: str
    standard_answer: str = ""
    question_text_en: str | None = None
    standard_answer_en: str | None = None
    # 该题对应的目标岗位，只能是 TARGET_ROLES 里的值，没有匹配的岗位就留空
    role: str | None = None
    difficulty_level: DifficultyLevel = "not_stated"
    company: str | None = None
    collected_at: datetime
    question_embedding: list[float] | None = None
    skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str | None) -> str | None:
        if value is not None and value not in _TARGET_ROLE_SET:
            raise ValueError(f"role must be chosen from TARGET_ROLES or null, invalid: {value!r}")
        return value
