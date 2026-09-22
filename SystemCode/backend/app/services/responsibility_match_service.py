from app.core.config import settings
from app.matching.embedding_provider import SentenceTransformerEmbeddingProvider
from app.matching.responsibility_scorer import ResponsibilityScorer
from app.schemas.match import ResponsibilityScoreRequest, ResponsibilityScoreResponse


class ResponsibilityMatchService:
    def __init__(self, scorer: ResponsibilityScorer | None = None) -> None:
        self.scorer = scorer or ResponsibilityScorer(
            embedding_provider=SentenceTransformerEmbeddingProvider(
                settings.responsibility_embedding_model
            ),
            similarity_floor=settings.responsibility_similarity_floor,
            similarity_full=settings.responsibility_similarity_full,
        )

    def score(self, request: ResponsibilityScoreRequest) -> ResponsibilityScoreResponse:
        return self.scorer.score(request.candidate, request.job)
