from app.parsers.text_parser import extract_skills
from app.schemas.job import JobAnalysis, JobAnalysisRequest


class JobService:
    def analyze(self, request: JobAnalysisRequest) -> JobAnalysis:
        constraints: list[str] = []
        if request.location:
            constraints.append(f"location:{request.location}")
        if request.degree_required:
            constraints.append(f"degree:{request.degree_required}")
        required_skills = extract_skills(request.description)
        return JobAnalysis(
            job_id=request.job_id,
            title=request.title,
            company=request.company,
            required_skills=required_skills,
            preferred_skills=[],
            constraints=constraints,
            summary=(
                f"{request.title} at {request.company} requires "
                f"{len(required_skills)} detected skills."
            ),
        )
