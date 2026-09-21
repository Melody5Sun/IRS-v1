from fastapi import APIRouter

from app.schemas.match import SkillScoreRequest, SkillScoreResponse
from app.services.skill_match_service import SkillMatchService


router = APIRouter()
skill_match_service = SkillMatchService()


@router.post("/skills", response_model=SkillScoreResponse)
def score_skills(request: SkillScoreRequest) -> SkillScoreResponse:
    return skill_match_service.score(request)
