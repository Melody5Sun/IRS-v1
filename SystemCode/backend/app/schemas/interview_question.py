from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import DifficultyLevel
from app.schemas.profile import TARGET_ROLES


# 题目不对应任何具体岗位（数据结构/算法、C/C++/Java/Python 语言基础等通用题）时的归类标签
GENERAL_PROGRAMMING_ROLE = "Basic Programming Problems"
_ALLOWED_ROLES = frozenset(TARGET_ROLES) | {GENERAL_PROGRAMMING_ROLE}


class InterviewQuestion(BaseModel):
    id: int | None = None
    source: str
    external_id: str
    question_text: str
    standard_answer: str = ""
    question_text_en: str | None = None
    standard_answer_en: str | None = None
    # 该题对应的目标岗位列表，取值来自 TARGET_ROLES；没有匹配的岗位时为 ["Basic Programming Problems"]
    roles: list[str] = Field(default_factory=lambda: [GENERAL_PROGRAMMING_ROLE])
    difficulty_level: DifficultyLevel = "not_stated"
    company: str | None = None
    collected_at: datetime
    question_embedding: list[float] | None = None
    skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

    @field_validator("roles")
    @classmethod
    def _validate_roles(cls, value: list[str]) -> list[str]:
        invalid = [role for role in value if role not in _ALLOWED_ROLES]
        if invalid:
            raise ValueError(f"roles must be chosen from TARGET_ROLES or {GENERAL_PROGRAMMING_ROLE!r}, invalid: {invalid!r}")
        return value or [GENERAL_PROGRAMMING_ROLE]
