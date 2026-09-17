from datetime import datetime, timezone
import re

from app.parsers.job_skill_parser import find_job_skill_matches
from app.schemas.common import (
    CandidateType,
    Degree,
    EmploymentType,
    Location,
    SeniorityLevel,
    VisaSponsorship,
)
from app.schemas.job import JobAnalysisRequest, JobPosting, JobRequirementDocument


SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")
INFERRED_SKILL_RULES = [
    (("data analyst", "data analysis", "business analyst", "metrics", "insights"), ("analytics", "sql", "excel")),
    (("dashboard", "visualization", "reporting"), ("data visualization", "tableau", "excel")),
    (("data engineer", "data pipeline", "etl", "warehouse"), ("data engineering", "sql", "python")),
    (("machine learning", " ai ", "artificial intelligence", "llm", "recommendation"), ("machine learning", "python")),
    (("nlp", "natural language"), ("nlp", "python")),
    (("backend", "back-end", "server-side", "microservice"), ("api development", "databases", "microservices")),
    (("frontend", "front-end", "web application", "user interface"), ("html", "css", "javascript")),
    (("mobile", "ios", "android"), ("android", "swift", "kotlin")),
    (("site reliability", "sre", "infrastructure", "platform engineer", "devops"), ("linux", "cloud computing", "ci/cd")),
    (("container", "orchestration"), ("containerization", "docker", "kubernetes")),
    (("cloud", "aws", "azure", "gcp"), ("cloud computing",)),
    (("security", "cyber", "threat", "vulnerability"), ("cybersecurity", "threat detection")),
    (("quant", "trading", "low latency", "market data"), ("algorithms", "python", "statistics")),
    (("product manager", "product management", "product builder"), ("analytics", "ab testing", "ui/ux")),
]


class JobRequirementParser:
    def parse_request(self, request: JobAnalysisRequest) -> JobRequirementDocument:
        return self._parse(
            company=request.company,
            title=request.title,
            description=request.description,
            location_text=request.location,
            source_job_id=request.job_id,
            fallback_employment_type=request.employment_type if hasattr(request, "employment_type") else None,
            fallback_degree=request.degree_required,
            fallback_visa=self._visa_from_bool(request.visa_sponsorship),
        )

    def parse_posting(self, posting: JobPosting) -> JobRequirementDocument:
        return self._parse(
            company=posting.company,
            title=posting.title,
            description=posting.description,
            location_text=posting.location,
            source_job_id=posting.external_id,
            job_id=posting.id,
            fallback_employment_type=posting.employment_type,
        )

    def _parse(
        self,
        company: str,
        title: str,
        description: str,
        location_text: str | None,
        source_job_id: str | None = None,
        job_id: int | None = None,
        fallback_employment_type: str | None = None,
        fallback_degree: str | None = None,
        fallback_visa: VisaSponsorship = "not_stated",
    ) -> JobRequirementDocument:
        combined_text = f"{title}\n{description}"
        sentences = self._sentences(combined_text)
        required_skills, preferred_skills = self._extract_skills(sentences)

        return JobRequirementDocument(
            job_id=job_id,
            source_job_id=source_job_id,
            company=company,
            title=title,
            summary=self._summary(description),
            employment_type=self._employment_type(combined_text, fallback_employment_type),
            candidate_type=self._candidate_type(combined_text),
            seniority_level=self._seniority_level(combined_text),
            location=self._location(location_text),
            remote_policy=self._remote_policy(combined_text),
            visa_sponsorship=self._visa_sponsorship(combined_text, fallback_visa),
            work_authorization_notes=self._work_authorization_notes(sentences),
            degree_required=self._degree_required(combined_text, fallback_degree),
            major_required=self._major_required(combined_text),
            responsibilities=self._responsibilities(sentences),
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            keywords=self._keywords(required_skills, preferred_skills),
            source_evidence=self._source_evidence(sentences),
            analysis_version="1.0",
            analysis_method="rule_based",
            analyzed_at=datetime.now(timezone.utc),
        )

    def _sentences(self, text: str) -> list[str]:
        return [
            sentence.strip(" -•\t")
            for sentence in SENTENCE_PATTERN.split(text)
            if sentence.strip(" -•\t")
        ]

    def _summary(self, description: str) -> str:
        sentences = self._sentences(description)
        return sentences[0][:300] if sentences else ""

    def _employment_type(self, text: str, fallback: str | None) -> EmploymentType:
        normalized = text.lower()
        fallback_normalized = (fallback or "").lower()
        if "intern" in normalized or "intern" in fallback_normalized:
            return "internship"
        if "part-time" in normalized or "part time" in normalized:
            return "part_time"
        if "contract" in normalized:
            return "contract"
        if "freelance" in normalized:
            return "freelance"
        if "full-time" in normalized or "full time" in normalized or "permanent" in fallback_normalized:
            return "full_time"
        return "not_stated"

    def _candidate_type(self, text: str) -> CandidateType:
        normalized = text.lower()
        if "student" in normalized or "intern" in normalized:
            return "student"
        if "graduate" in normalized or "new grad" in normalized or "fresh graduate" in normalized:
            return "new_graduate"
        if "experienced" in normalized:
            return "experienced"
        return "not_stated"

    def _seniority_level(self, text: str) -> SeniorityLevel:
        normalized = text.lower()
        if "intern" in normalized:
            return "intern"
        if "entry level" in normalized or "new grad" in normalized or "graduate" in normalized:
            return "entry_level"
        if "junior" in normalized:
            return "junior"
        if "senior" in normalized or "lead" in normalized:
            return "senior"
        return "not_stated"

    def _location(self, location_text: str | None) -> Location | None:
        if not location_text:
            return None
        parts = [part.strip() for part in location_text.split(",") if part.strip()]
        if not parts:
            return None
        country = "Singapore" if any(part.lower() == "singapore" for part in parts) else parts[-1]
        city = "Singapore" if "singapore" in location_text.lower() else parts[0]
        return Location(city=city, country=country)

    def _remote_policy(self, text: str):
        normalized = text.lower()
        if "hybrid" in normalized:
            return "hybrid"
        if "remote" in normalized:
            return "remote"
        if "onsite" in normalized or "on-site" in normalized:
            return "onsite"
        return "not_stated"

    def _visa_from_bool(self, visa_sponsorship: bool | None) -> VisaSponsorship:
        if visa_sponsorship is True:
            return "provided"
        if visa_sponsorship is False:
            return "not_provided"
        return "not_stated"

    def _visa_sponsorship(self, text: str, fallback: VisaSponsorship) -> VisaSponsorship:
        normalized = text.lower()
        if "visa sponsorship" in normalized or "sponsor" in normalized:
            if "not sponsor" in normalized or "no sponsorship" in normalized or "unable to sponsor" in normalized:
                return "not_provided"
            return "provided"
        if "singapore citizen" in normalized or "permanent resident" in normalized:
            return "not_provided"
        return fallback

    def _work_authorization_notes(self, sentences: list[str]) -> str | None:
        for sentence in sentences:
            normalized = sentence.lower()
            if "visa" in normalized or "sponsor" in normalized or "citizen" in normalized:
                return sentence
        return None

    def _degree_required(self, text: str, fallback: str | None) -> Degree:
        normalized = f"{text} {fallback or ''}".lower()
        if "phd" in normalized or "doctorate" in normalized:
            return "phd"
        if "master" in normalized:
            return "master"
        if "bachelor" in normalized or "undergraduate" in normalized:
            return "bachelor"
        if "diploma" in normalized:
            return "diploma"
        return "not_stated"

    def _major_required(self, text: str) -> list[str]:
        normalized = text.lower()
        majors = []
        for major in [
            "computer science",
            "information systems",
            "software engineering",
            "data science",
            "cybersecurity",
            "computer engineering",
        ]:
            if major in normalized:
                majors.append(major)
        return majors

    def _extract_skills(self, sentences: list[str]) -> tuple[list[str], list[str]]:
        required: dict[str, None] = {}
        preferred: dict[str, None] = {}
        full_text = " ".join(sentences)
        for sentence in sentences:
            normalized_sentence = sentence.lower()
            importance = self._skill_importance(normalized_sentence)
            for skill, _alias in find_job_skill_matches(sentence):
                target = preferred if importance == "preferred" else required
                other = required if importance == "preferred" else preferred
                if skill not in target and skill not in other:
                    target[skill] = None
        for skill in self._infer_skills_from_context(full_text):
            if skill not in required and skill not in preferred:
                required[skill] = None
        return list(required.keys()), list(preferred.keys())

    def _infer_skills_from_context(self, text: str) -> list[str]:
        normalized = f" {text.lower()} "
        inferred: dict[str, None] = {}
        for markers, skills in INFERRED_SKILL_RULES:
            if any(marker in normalized for marker in markers):
                for skill in skills:
                    inferred[skill] = None

        if len(text) < 800:
            limit = 4
        elif len(text) < 2000:
            limit = 6
        else:
            limit = 8
        return list(inferred.keys())[:limit]

    def _skill_importance(self, sentence: str) -> str:
        preferred_markers = ("preferred", "nice to have", "plus", "bonus", "advantage")
        if any(marker in sentence for marker in preferred_markers):
            return "preferred"
        return "required"

    def _responsibilities(self, sentences: list[str]) -> list[str]:
        markers = ("build", "develop", "design", "maintain", "work with", "collaborate", "support")
        responsibilities = [
            sentence
            for sentence in sentences
            if any(marker in sentence.lower() for marker in markers)
        ]
        return responsibilities[:8]

    def _keywords(self, required_skills: list[str], preferred_skills: list[str]) -> list[str]:
        return sorted({skill for skill in [*required_skills, *preferred_skills]})

    def _source_evidence(self, sentences: list[str]) -> list[str]:
        evidence_markers = ("required", "preferred", "qualification", "responsibil", "experience")
        return [
            sentence
            for sentence in sentences
            if any(marker in sentence.lower() for marker in evidence_markers)
        ][:10]
