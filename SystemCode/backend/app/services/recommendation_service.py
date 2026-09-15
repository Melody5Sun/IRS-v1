from app.matching.scorer import RecommendationScorer
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse


class RecommendationService:
    def __init__(self, scorer: RecommendationScorer | None = None) -> None:
        self.scorer = scorer or RecommendationScorer()

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        recommendations = [
            self.scorer.score(request.candidate, job)
            for job in request.jobs
        ]
        recommendations.sort(key=lambda item: item.score, reverse=True)
        return RecommendationResponse(recommendations=recommendations)
