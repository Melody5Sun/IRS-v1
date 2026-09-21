from pydantic import BaseModel, Field

from app.schemas.match import SkillScoreResponse


class RankedJob(BaseModel):
    job_id: int | None = None
    company: str
    title: str
    # 技能图谱评分的原始返回；目前只含技能部分（partial_score 最高 65），不是最终匹配分
    skill_score: SkillScoreResponse


class RankingResponse(BaseModel):
    # 统计沿用规则筛选的口径，见 RulesScreeningResponse
    total_jobs: int
    passed_count: int
    rejected_by_rule: dict[str, int] = Field(default_factory=dict)
    # 只含通过硬约束的岗位，按 skill_score.partial_score 降序
    results: list[RankedJob] = Field(default_factory=list)
