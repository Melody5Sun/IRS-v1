import json

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes import resumes as resumes_route
from app.main import app
from app.parsers.llm_resume_parser import LLMResumeParser, ResumeParsingError
from app.parsers.resume_parser import ResumeParser
from app.services.resume_service import ResumeService

client = TestClient(app)


class FakeChatClient:
    """按调用顺序依次返回预设的响应，模拟 LLM 输出，测试里不打真实 API。"""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        return self._responses.pop(0)


def _use_fake_llm(monkeypatch: pytest.MonkeyPatch, responses: list[str]) -> None:
    fake_parser = LLMResumeParser(client=FakeChatClient(responses))
    fake_service = ResumeService(parser=ResumeParser(llm_parser=fake_parser))
    monkeypatch.setattr(resumes_route, "resume_service", fake_service)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_parse_resume_extracts_structured_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    llm_response = json.dumps(
        {
            "name": "Jane Tan",
            "email": "jane@example.com",
            "phone": "+65 9123 4567",
            "location": {"city": "Singapore", "country": "Singapore"},
            "visa_status": "student_pass",
            "desired_position": "Software Engineer Intern",
            "experiences": [
                {
                    "company": "Acme",
                    "title": "Software Engineer Intern",
                    "employment_type": "internship",
                    "start_date": "2024-05",
                    "end_date": "2024-08",
                    "description": "Built APIs with FastAPI.",
                    "country": "Singapore",
                }
            ],
            "skills": [{"name": "Python", "level": "advanced"}],
            "educations": [
                {
                    "institution": "NUS",
                    "entry_type": "degree",
                    "degree": "bachelor",
                    "major": "Computer Science",
                    "start_date": "2022-08",
                    "end_date": "2026-05",
                    "country": "Singapore",
                }
            ],
        }
    )
    _use_fake_llm(monkeypatch, [llm_response])

    response = client.post(
        "/api/v1/resumes/parse",
        json={"text": "Jane Tan\njane@example.com\nSoftware Engineer Intern at Acme..."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Jane Tan"
    assert body["visa_status"] == "student_pass"
    assert body["requires_sponsorship"] is True
    assert body["experiences"][0]["employment_type"] == "internship"
    assert body["skills"][0]["level"] == "advanced"
    assert body["educations"][0]["entry_type"] == "degree"


def test_parse_resume_requires_sponsorship_false_for_citizen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llm_response = json.dumps({"name": "Alex Lee", "visa_status": "singapore_citizen"})
    _use_fake_llm(monkeypatch, [llm_response])

    response = client.post("/api/v1/resumes/parse", json={"text": "Alex Lee, Singaporean..."})

    assert response.status_code == 200
    assert response.json()["requires_sponsorship"] is False


def test_parse_resume_retries_once_on_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    valid_response = json.dumps({"name": "Retry Candidate", "visa_status": "permanent_resident"})
    _use_fake_llm(monkeypatch, ["not valid json", valid_response])

    response = client.post("/api/v1/resumes/parse", json={"text": "some resume text"})

    assert response.status_code == 200
    assert response.json()["name"] == "Retry Candidate"
    assert response.json()["requires_sponsorship"] is False


def test_parse_resume_raises_after_second_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    _use_fake_llm(monkeypatch, ["not valid json", "still not valid json"])

    with pytest.raises(ResumeParsingError):
        client.post("/api/v1/resumes/parse", json={"text": "some resume text"})


def test_recommendations_rank_matching_job_first() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "candidate": {
                "name": "Jane Tan",
                "skills": ["python", "react", "sql"],
                "education": ["Master of Computing"],
                "experience_years": 2,
                "work_authorization": "student_pass",
            },
            "jobs": [
                {
                    "job_id": "job-1",
                    "title": "Software Engineer Intern",
                    "company": "Acme",
                    "description": "Build APIs with Python, FastAPI and SQL.",
                    "min_experience_years": 1,
                    "visa_sponsorship": True,
                },
                {
                    "job_id": "job-2",
                    "title": "Frontend Intern",
                    "company": "Beta",
                    "description": "Build UI with TypeScript and CSS.",
                    "min_experience_years": 1,
                    "visa_sponsorship": True,
                },
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendations"][0]["job_id"] == "job-1"
    assert body["recommendations"][0]["eligible"] is True
