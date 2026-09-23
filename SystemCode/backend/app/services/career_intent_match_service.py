from app.core.config import settings
from app.matching.career_intent_scorer import CareerIntentScorer
from app.matching.embedding_provider import SentenceTransformerEmbeddingProvider
from app.schemas.match import CareerIntentScoreRequest, CareerIntentScoreResponse


class CareerIntentMatchService:
    def __init__(self, scorer: CareerIntentScorer | None = None) -> None:
        self.scorer = scorer or CareerIntentScorer(
            embedding_provider=SentenceTransformerEmbeddingProvider(
                settings.career_intent_embedding_model
            ),
            taxonomy_path=settings.role_taxonomy_path,
            embedding_cache_path=settings.role_embedding_cache_path,
            metadata_path=settings.role_embedding_metadata_path,
            model_name=settings.career_intent_embedding_model,
            similarity_floor=settings.career_intent_similarity_floor,
            similarity_full=settings.career_intent_similarity_full,
        )

    def score(self, request: CareerIntentScoreRequest) -> CareerIntentScoreResponse:
        return self.scorer.score(request.target_roles, request.job)
