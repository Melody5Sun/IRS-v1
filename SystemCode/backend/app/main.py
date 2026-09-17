from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.knowledge.mind_ontology import get_mind_knowledge_graph


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for resume parsing and explainable job recommendations.",
    )
    app.state.mind_knowledge_graph = get_mind_knowledge_graph()
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
