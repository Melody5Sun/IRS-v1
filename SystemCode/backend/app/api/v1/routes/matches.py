from fastapi import APIRouter

from app.schemas.match import (
    ResponsibilityScoreRequest,
    ResponsibilityScoreResponse,
    SkillScoreRequest,
    SkillScoreResponse,
)
from app.services.responsibility_match_service import ResponsibilityMatchService
from app.services.skill_match_service import SkillMatchService


router = APIRouter()
skill_match_service = SkillMatchService()
responsibility_match_service = ResponsibilityMatchService()


@router.post("/skills", response_model=SkillScoreResponse)
def score_skills(request: SkillScoreRequest) -> SkillScoreResponse:
    return skill_match_service.score(request)


@router.post("/responsibilities", response_model=ResponsibilityScoreResponse)
def score_responsibilities(
    request: ResponsibilityScoreRequest,
) -> ResponsibilityScoreResponse:
    return responsibility_match_service.score(request)
