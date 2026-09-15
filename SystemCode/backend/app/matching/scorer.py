from app.schemas.job import JobAnalysisRequest
from app.schemas.recommendation import RecommendationItem
from app.schemas.resume import ResumeProfile
from app.services.job_service import JobService


class RecommendationScorer:
    def __init__(self, job_service: JobService | None = None) -> None:
        self.job_service = job_service or JobService()

    def score(self, candidate: ResumeProfile, job: JobAnalysisRequest) -> RecommendationItem:
        analysis = self.job_service.analyze(job)
        candidate_skills = set(candidate.skills)
        required_skills = set(analysis.required_skills)
        matched_skills = sorted(candidate_skills & required_skills)
        missing_skills = sorted(required_skills - candidate_skills)
        eligible, constraint_reasons = self._check_constraints(candidate, job)

        skill_score = len(matched_skills) / len(required_skills) if required_skills else 0.5
        score = skill_score if eligible else min(skill_score, 0.35)

        reasons = [
            f"Matched {len(matched_skills)} of {len(required_skills)} detected required skills.",
            *constraint_reasons,
        ]
        if missing_skills:
            reasons.append(f"Missing skills: {', '.join(missing_skills)}.")

        return RecommendationItem(
            job_id=job.job_id,
            title=job.title,
            company=job.company,
            score=round(score, 2),
            eligible=eligible,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            reasons=reasons,
        )

    def _check_constraints(
        self,
        candidate: ResumeProfile,
        job: JobAnalysisRequest,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        eligible = True

        if job.min_experience_years is not None:
            candidate_years = candidate.experience_years or 0
            if candidate_years < job.min_experience_years:
                eligible = False
                reasons.append(
                    f"Experience below requirement: {candidate_years} < {job.min_experience_years} years."
                )

        if job.visa_sponsorship is False and candidate.work_authorization == "requires_sponsorship":
            eligible = False
            reasons.append("Candidate requires sponsorship but the job does not provide it.")

        if eligible:
            reasons.append("Hard constraints passed.")

        return eligible, reasons
