from pydantic import BaseModel, Field

from app.schemas.match import (
    CareerIntentScoreResponse,
    ResponsibilityScoreResponse,
    SkillScoreResponse,
)


class OverallScore(BaseModel):
    calculable: bool
    active_core_weight: float = Field(..., ge=0, le=100)
    effective_weights: dict[str, float] = Field(default_factory=dict)
    normalized_contributions: dict[str, float] = Field(default_factory=dict)
    core_score: float = Field(..., ge=0, le=100)
    preferred_bonus: float = Field(..., ge=0, le=5)
    final_score: float = Field(..., ge=0, le=100)


class RankedJob(BaseModel):
    job_id: int | None = None
    company: str
    title: str
    skill_score: SkillScoreResponse
    responsibility_score: ResponsibilityScoreResponse
    career_intent_score: CareerIntentScoreResponse
    overall_score: OverallScore


class RankingResponse(BaseModel):
    # 统计沿用规则筛选的口径，见 RulesScreeningResponse
    total_jobs: int
    passed_count: int
    rejected_by_rule: dict[str, int] = Field(default_factory=dict)
    # 只含通过硬约束的岗位，按 overall_score.final_score 降序
    results: list[RankedJob] = Field(default_factory=list)
