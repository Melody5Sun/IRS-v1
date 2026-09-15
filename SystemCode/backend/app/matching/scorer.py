import re
from datetime import date

from app.parsers.text_parser import extract_skills
from app.schemas.job import JobAnalysisRequest
from app.schemas.recommendation import RecommendationItem
from app.schemas.resume import Experience, ResumeDocument
from app.services.job_service import JobService

DATE_PATTERN = re.compile(r"(\d{4})(?:-(\d{1,2}))?")


def _month_index(value: str | None, *, is_end: bool) -> int | None:
    if not value:
        return None
    if value.strip().lower() == "present":
        today = date.today()
        return today.year * 12 + today.month - 1
    match = DATE_PATTERN.fullmatch(value.strip())
    if not match:
        return None
    # ponytail: 只写了年份时按整年算（起始 1 月、结束 12 月），同年起止的短经历会被高估
    month = int(match.group(2)) if match.group(2) else (12 if is_end else 1)
    return int(match.group(1)) * 12 + month - 1


def calculate_experience_years(experiences: list[Experience]) -> float:
    # 按月份集合累计，时间重叠的经历不会被重复计算
    months: set[int] = set()
    for experience in experiences:
        start = _month_index(experience.start_date, is_end=False)
        if start is None:
            continue
        end = _month_index(experience.end_date, is_end=True)
        months.update(range(start, (start if end is None else end) + 1))
    return round(len(months) / 12, 1)


class RecommendationScorer:
    def __init__(self, job_service: JobService | None = None) -> None:
        self.job_service = job_service or JobService()

    def score(self, candidate: ResumeDocument, job: JobAnalysisRequest) -> RecommendationItem:
        analysis = self.job_service.analyze(job)
        # 用和 JD 同一套词表归一化（"Python" -> "python"），两边技能名才对得上
        candidate_skills = set(extract_skills("\n".join(candidate.skills)))
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
        candidate: ResumeDocument,
        job: JobAnalysisRequest,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        eligible = True

        if job.min_experience_years is not None:
            candidate_years = calculate_experience_years(candidate.experiences)
            if candidate_years < job.min_experience_years:
                eligible = False
                reasons.append(
                    f"Experience below requirement: {candidate_years} < {job.min_experience_years} years."
                )

        if job.visa_sponsorship is False and candidate.requires_sponsorship:
            eligible = False
            reasons.append("Candidate requires sponsorship but the job does not provide it.")

        if eligible:
            reasons.append("Hard constraints passed.")

        return eligible, reasons
