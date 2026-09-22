from app.schemas.job import JobRequirementDocument
from app.schemas.match import ConstraintCheck, MatchResult, SkillMatch
from app.schemas.resume import ResumeDocument


def test_resume_document_keeps_normalized_skill_list() -> None:
    resume = ResumeDocument(skills=["python", "docker"])

    assert resume.skills == ["python", "docker"]


def test_job_requirement_document_captures_matching_fields() -> None:
    document = JobRequirementDocument(
        company="ShopBack",
        title="Software Engineer Intern",
        employment_type="internship",
        candidate_type="student",
        degree_required="bachelor",
        required_skills=["python"],
        preferred_skills=["docker"],
    )

    assert document.employment_type == "internship"
    assert document.required_skills == ["python"]
    assert document.preferred_skills == ["docker"]


def test_match_result_keeps_constraints_and_explanations() -> None:
    result = MatchResult(
        job_id=1,
        score=0.82,
        eligible=True,
        constraint_checks=[
            ConstraintCheck(
                name="degree_required",
                status="unknown",
                reason="The JD does not state a degree requirement.",
            )
        ],
        matched_required_skills=[
            SkillMatch(name="python", source="resume.skills", evidence="Python project listed.")
        ],
        missing_required_skills=["sql"],
        reasons=["Matched Python but SQL is missing."],
        improvement_suggestions=["Add SQL project evidence if available."],
    )

    assert result.eligible is True
    assert result.constraint_checks[0].status == "unknown"
    assert result.missing_required_skills == ["sql"]
