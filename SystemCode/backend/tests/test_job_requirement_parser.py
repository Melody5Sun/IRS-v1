from datetime import datetime, timezone

from app.db.sqlite import connect
from app.parsers.job_requirement_parser import JobRequirementParser
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobAnalysisRequest, JobPosting
from app.schemas.profile import TARGET_INDUSTRIES
from app.services.job_requirement_service import JobRequirementService


def test_job_requirement_parser_extracts_core_matching_fields() -> None:
    parser = JobRequirementParser()
    document = parser.parse_request(
        request=JobAnalysisRequest(
            job_id="job-1",
            company="ShopBack",
            title="Software Engineer Intern",
            location="Singapore",
            description=(
                "We are looking for an undergraduate student to build backend services. "
                "Required experience with Python, SQL and FastAPI. "
                "Docker is a plus. "
                "Bachelor degree in Computer Science is preferred."
            ),
        )
    )

    required_skill_names = set(document.required_skills)
    preferred_skill_names = set(document.preferred_skills)

    assert document.employment_type == "internship"
    assert document.industry == "E-commerce"
    assert document.candidate_type == "student"
    assert document.degree_required == "bachelor"
    assert "python" in required_skill_names
    assert "sql" in required_skill_names
    assert "fastapi" in required_skill_names
    assert "docker" in preferred_skill_names
    assert {"seniority_level", "analysis_version", "analysis_method", "analyzed_at"}.isdisjoint(
        document.model_dump()
    )


def test_job_repository_saves_job_requirement_analysis(tmp_path) -> None:
    repository = JobRepository(tmp_path / "careerpilot.db")
    now = datetime.now(timezone.utc)
    job = JobPosting(
        source="test_source",
        company="Stripe",
        external_id="job-1",
        title="Data Engineer Intern",
        location="Singapore",
        description="Build data pipelines with Python and SQL.",
        url="https://example.com/job-1",
        collected_at=now,
        last_seen_at=now,
        content_hash="hash-job-1",
    )
    repository.upsert_many([job])
    stored_job = repository.list_jobs()[0]

    document = JobRequirementParser().parse_posting(stored_job)
    repository.save_job_analysis(document)

    assert document.job_id == stored_job.id
    with connect(repository.db_path) as connection:
        row = connection.execute(
            "SELECT company, industry FROM company_industries WHERE normalized_company = ?",
            ("stripe",),
        ).fetchone()
        analysis_columns = {
            column["name"]
            for column in connection.execute("PRAGMA table_info(job_analysis)").fetchall()
        }
    assert row["company"] == "Stripe"
    assert row["industry"] == "Financial Technology (FinTech)"
    assert {
        "industry",
        "seniority_level",
        "analysis_version",
        "analysis_method",
        "analyzed_at",
    }.isdisjoint(
        analysis_columns
    )


def test_job_requirement_parser_infers_skills_from_context() -> None:
    parser = JobRequirementParser()
    document = parser.parse_request(
        request=JobAnalysisRequest(
            job_id="job-2",
            company="Acme",
            title="Site Reliability Engineer Intern",
            location="Singapore",
            description=(
                "Join the infrastructure team to improve production reliability, "
                "support cloud platforms, and automate deployment workflows."
            ),
        )
    )

    assert {"linux", "cloud computing", "ci/cd"}.issubset(set(document.required_skills))


def test_job_industry_uses_company_not_job_title() -> None:
    parser = JobRequirementParser()
    document = parser.parse_request(
        request=JobAnalysisRequest(
            job_id="job-ai",
            company="Stripe",
            title="Machine Learning Engineer Intern",
            location="Singapore",
            description="Develop models with Python for internal products.",
        )
    )

    assert document.industry == "Financial Technology (FinTech)"


def test_industry_table_contains_the_fixed_taxonomy(tmp_path) -> None:
    repository = JobRepository(tmp_path / "careerpilot.db")
    repository.count_job_analysis()

    with connect(repository.db_path) as connection:
        industries = {
            row["name"]
            for row in connection.execute("SELECT name FROM industries").fetchall()
        }

    assert industries == set(TARGET_INDUSTRIES)


def test_job_requirement_service_falls_back_when_gemini_is_not_configured(tmp_path) -> None:
    class DisabledGeminiService:
        def is_configured(self) -> bool:
            return False

    repository = JobRepository(tmp_path / "careerpilot.db")
    now = datetime.now(timezone.utc)
    job = JobPosting(
        source="test_source",
        company="TestCo",
        external_id="job-1",
        title="Software Engineer Intern",
        location="Singapore",
        description="Required experience with Python and SQL.",
        url="https://example.com/job-1",
        collected_at=now,
        last_seen_at=now,
        content_hash="hash-job-1",
    )
    repository.upsert_many([job])
    stored_job = repository.list_jobs()[0]
    service = JobRequirementService(
        repository=repository,
        gemini_service=DisabledGeminiService(),
    )

    document = service.analyze_stored_job(stored_job.id)

    assert document is not None
    assert document.industry == "Software & IT Services"
    assert set(document.required_skills) == {"python", "sql"}


def test_job_requirement_service_marks_jobs_without_skills_inactive(tmp_path) -> None:
    class DisabledGeminiService:
        def is_configured(self) -> bool:
            return False

    repository = JobRepository(tmp_path / "careerpilot.db")
    now = datetime.now(timezone.utc)
    job = JobPosting(
        source="test_source",
        company="TestCo",
        external_id="job-no-skills",
        title="Graduate Community Intern",
        location="Singapore",
        description="Support community events and coordinate stakeholder communications.",
        url="https://example.com/job-no-skills",
        collected_at=now,
        last_seen_at=now,
        content_hash="hash-job-no-skills",
    )
    repository.upsert_many([job])
    service = JobRequirementService(
        repository=repository,
        gemini_service=DisabledGeminiService(),
    )

    analyzed_count = service.analyze_active_jobs()
    inactive_jobs = repository.list_jobs(status="inactive")

    assert analyzed_count == 0
    assert repository.count_job_analysis() == 0
    assert len(inactive_jobs) == 1
    assert inactive_jobs[0].external_id == "job-no-skills"
