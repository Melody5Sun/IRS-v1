from app.parsers.text_parser import extract_skills
from app.schemas.job import JobAnalysis, JobAnalysisRequest


class JobParser:
    def analyze(self, request: JobAnalysisRequest) -> JobAnalysis:
        required_skills = extract_skills(request.description)
        constraints = self._extract_constraints(request)
        summary = f"{request.title} at {request.company} requires {len(required_skills)} detected skills."
        return JobAnalysis(
            job_id=request.job_id,
            title=request.title,
            company=request.company,
            required_skills=required_skills,
            preferred_skills=[],
            constraints=constraints,
            summary=summary,
        )

    def _extract_constraints(self, request: JobAnalysisRequest) -> list[str]:
        constraints: list[str] = []
        if request.location:
            constraints.append(f"location:{request.location}")
        if request.visa_sponsorship is not None:
            constraints.append(f"visa_sponsorship:{request.visa_sponsorship}")
        if request.degree_required:
            constraints.append(f"degree:{request.degree_required}")
        if request.min_experience_years is not None:
            constraints.append(f"min_experience_years:{request.min_experience_years}")
        return constraints
