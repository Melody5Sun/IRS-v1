from app.schemas.match import SkillScoreRequest
from app.schemas.profile import UserProfile
from app.schemas.ranking import RankedJob, RankingResponse
from app.services.rules_screening_service import RulesScreeningService
from app.services.skill_match_service import SkillMatchService


class RankingService:
    """先用规则引擎做硬约束初筛，规则引擎一跑完就把筛出的岗位交给技能图谱评分，再按分数排序。"""

    def __init__(
        self,
        rules_screening_service: RulesScreeningService,
        skill_match_service: SkillMatchService,
    ) -> None:
        self.rules_screening_service = rules_screening_service
        self.skill_match_service = skill_match_service

    def run(self, profile: UserProfile) -> RankingResponse:
        screened = self.rules_screening_service.run(profile)
        results = [
            RankedJob(
                job_id=job.job_id,
                company=job.company,
                title=job.title,
                skill_score=self.skill_match_service.score(SkillScoreRequest(candidate=profile.resume, job=job)),
            )
            for job in screened.jobs
        ]
        # 稳定排序：分数相同的岗位保持 job_id 升序
        results.sort(key=lambda item: item.skill_score.partial_score, reverse=True)
        return RankingResponse(
            total_jobs=screened.total_jobs,
            passed_count=screened.passed_count,
            rejected_by_rule=screened.rejected_by_rule,
            results=results,
        )
