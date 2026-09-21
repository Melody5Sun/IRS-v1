from pydantic import BaseModel, Field

from app.schemas.job import JobRequirementDocument


class RulesScreeningResponse(BaseModel):
    total_jobs: int  # 有分析记录的岗位总数（通过 + 被剔除）
    passed_count: int
    # 各规则单独剔除数：一个岗位可能被多条规则同时剔除，所以各项相加可能大于 total_jobs - passed_count
    rejected_by_rule: dict[str, int] = Field(default_factory=dict)
    # 只含通过全部硬约束的岗位，按 job_id 升序
    jobs: list[JobRequirementDocument] = Field(default_factory=list)
