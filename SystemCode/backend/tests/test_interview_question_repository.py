from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.schemas.interview_question import InterviewQuestion


def make_question(external_id: str = "q-1", question_text: str = "What is an Agent?") -> InterviewQuestion:
    return InterviewQuestion(
        source="test_source",
        external_id=external_id,
        question_text=question_text,
        standard_answer="An LLM-driven autonomous system.",
        question_text_en=question_text,
        standard_answer_en="An LLM-driven autonomous system.",
        role="Agent Engineer",
        difficulty_level="medium",
        company="TestCo",
        collected_at=datetime.now(timezone.utc),
        skills=["python", "rag"],
        keywords=["agent", "llm"],
    )


def test_upsert_many_inserts_and_lists_by_company(tmp_path) -> None:
    repository = InterviewQuestionRepository(tmp_path / "careerpilot.db")

    changed_count = repository.upsert_many([make_question()])
    questions = repository.list_questions(company="TestCo")

    assert changed_count == 1
    assert repository.count() == 1
    assert len(questions) == 1
    assert questions[0].question_text == "What is an Agent?"
    assert questions[0].question_text_en == "What is an Agent?"
    assert questions[0].standard_answer_en == "An LLM-driven autonomous system."
    assert questions[0].role == "Agent Engineer"
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


def test_upsert_many_allows_missing_english_version(tmp_path) -> None:
    repository = InterviewQuestionRepository(tmp_path / "careerpilot.db")
    question = make_question()
    question = question.model_copy(update={"question_text_en": None, "standard_answer_en": None})

    repository.upsert_many([question])
    stored = repository.list_questions()[0]

    assert stored.question_text_en is None
    assert stored.standard_answer_en is None


def test_upsert_many_allows_null_role_when_no_match(tmp_path) -> None:
    repository = InterviewQuestionRepository(tmp_path / "careerpilot.db")
    question = make_question().model_copy(update={"role": None})

    repository.upsert_many([question])

    assert repository.list_questions()[0].role is None


def test_role_must_be_chosen_from_target_roles() -> None:
    with pytest.raises(ValidationError):
        InterviewQuestion.model_validate(make_question().model_dump() | {"role": "Not A Real Role"})
