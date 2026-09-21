from pydantic import BaseModel, Field

from app.schemas.common import ConstraintStatus
from app.schemas.job import JobRequirementDocument
from app.schemas.resume import ResumeDocument


class ConstraintCheck(BaseModel):
    name: str
    status: ConstraintStatus
    reason: str


class SkillMatch(BaseModel):
    name: str
    source: str
    evidence: str | None = None


class MatchResult(BaseModel):
    resume_id: str | None = None
    job_id: int
    score: float = Field(..., ge=0, le=1)
    eligible: bool
    constraint_checks: list[ConstraintCheck] = Field(default_factory=list)
    matched_required_skills: list[SkillMatch] = Field(default_factory=list)
    matched_preferred_skills: list[SkillMatch] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)


class SkillScoreRequest(BaseModel):
    candidate: ResumeDocument
    job: JobRequirementDocument


class DirectSkillMatch(BaseModel):
    jd_skill: str
    candidate_skill: str


class GraphSkillMatch(BaseModel):
    jd_skill: str
    candidate_skill: str
    relation: str
    relation_score: float = Field(..., ge=0, le=1)
    path: list[str] = Field(default_factory=list)


class SkillScoreResponse(BaseModel):
    job_id: int | None = None
    required_skills_calculable: bool
    preferred_skills_available: bool
    required_direct_coverage: float = Field(..., ge=0, le=100)
    required_direct_points: float = Field(..., ge=0, le=40)
    required_graph_coverage: float = Field(..., ge=0, le=100)
    required_graph_points: float = Field(..., ge=0, le=20)
    preferred_direct_coverage: float = Field(..., ge=0, le=100)
    preferred_graph_coverage: float = Field(..., ge=0, le=100)
    preferred_skill_coverage: float = Field(..., ge=0, le=100)
    preferred_bonus: float = Field(..., ge=0, le=5)
    partial_score: float = Field(..., ge=0, le=65)
    direct_required_matches: list[DirectSkillMatch] = Field(default_factory=list)
    graph_required_matches: list[GraphSkillMatch] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    direct_preferred_matches: list[DirectSkillMatch] = Field(default_factory=list)
    graph_preferred_matches: list[GraphSkillMatch] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
