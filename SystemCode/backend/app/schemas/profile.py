from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.resume import ResumeDocument

# 现场 / 混合 / 远程
WorkMode = Literal["onsite", "hybrid", "remote"]


class JobSearchConstraints(BaseModel):
    target_roles: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    work_modes: list[WorkMode] = Field(default_factory=list)
    # 补充说明（选填）；上传简历时用简历里的自我介绍预填
    notes: str = ""


class UserProfile(BaseModel):
    # 画像沿用简历 schema：parse-pdf 解析结果，用户可在前端修改补全
    resume: ResumeDocument
    constraints: JobSearchConstraints = Field(default_factory=JobSearchConstraints)
