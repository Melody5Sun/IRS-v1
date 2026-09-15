from fastapi import APIRouter

from app.api.v1.routes import health, jobs, recommendations, resumes

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"],
)
