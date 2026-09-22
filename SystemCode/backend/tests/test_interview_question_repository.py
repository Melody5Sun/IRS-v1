from datetime import datetime, timezone

from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.schemas.interview_question import InterviewQuestion


def make_question(external_id: str = "q-1", question_text: str = "What is an Agent?") -> InterviewQuestion:
    return InterviewQuestion(
        source="test_source",
        external_id=external_id,
        question_text=question_text,
        standard_answer="An LLM-driven autonomous system.",
        difficulty_level="medium",
        company="TestCo",
        collected_at=datetime.now(timezone.utc),
        skills=["python", "rag"],
        keywords=["Agent 核心面试题"],
    )


def test_upsert_many_inserts_and_lists_by_company(tmp_path) -> None:
    repository = InterviewQuestionRepository(tmp_path / "careerpilot.db")

    changed_count = repository.upsert_many([make_question()])
    questions = repository.list_questions(company="TestCo")

    assert changed_count == 1
    assert repository.count() == 1
    assert len(questions) == 1
    assert questions[0].question_text == "What is an Agent?"
    assert questions[0].skills == ["python", "rag"]
    assert questions[0].difficulty_level == "medium"


def test_upsert_many_is_idempotent_on_source_and_external_id(tmp_path) -> None:
    repository = InterviewQuestionRepository(tmp_path / "careerpilot.db")

    repository.upsert_many([make_question()])
    changed_count = repository.upsert_many([make_question()])

    assert changed_count == 0
    assert repository.count() == 1


def test_upsert_many_updates_changed_content(tmp_path) -> None:
    repository = InterviewQuestionRepository(tmp_path / "careerpilot.db")

    repository.upsert_many([make_question()])
    updated = make_question(question_text="What is an Agent, exactly?")
    changed_count = repository.upsert_many([updated])

    assert changed_count == 1
    assert repository.count() == 1
    assert repository.list_questions()[0].question_text == "What is an Agent, exactly?"
