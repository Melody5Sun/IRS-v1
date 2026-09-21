from app.matching.skill_scorer import SkillScorer
from app.schemas.match import SkillScoreRequest, SkillScoreResponse


class SkillMatchService:
    def __init__(self, scorer: SkillScorer | None = None) -> None:
        self.scorer = scorer or SkillScorer()

    def score(self, request: SkillScoreRequest) -> SkillScoreResponse:
        return self.scorer.score(request.candidate, request.job)
