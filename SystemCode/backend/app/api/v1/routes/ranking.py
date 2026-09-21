from fastapi import APIRouter

from app.schemas.profile import UserProfile
from app.schemas.ranking import RankingResponse
from app.services.ranking_service import RankingService
from app.services.rules_screening_service import RulesScreeningService
from app.services.skill_match_service import SkillMatchService

router = APIRouter()
ranking_service = RankingService(RulesScreeningService(), SkillMatchService())


@router.post("", response_model=RankingResponse)
def rank_jobs(profile: UserProfile) -> RankingResponse:
    # 入口：规则引擎初筛 -> 技能图谱评分 -> 按分数降序；请求体就是 GET /profile 返回的画像
    return ranking_service.run(profile)
