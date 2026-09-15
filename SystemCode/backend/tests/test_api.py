import json

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes import resumes as resumes_route
from app.main import app
from app.matching.scorer import calculate_experience_years
from app.parsers.llm_resume_parser import SYSTEM_PROMPT, LLMResumeParser, ResumeParsingError
from app.parsers.resume_parser import ResumeParser
from app.schemas.resume import Experience, ResumeDocument
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
            "visa_status": "student_pass",
            "research": [
                {
                    "title": "Federated Learning for Edge Devices",
                    "institution": "NUS",
                    "summary": "Studied communication-efficient aggregation strategies.",
                    "start_date": "2025-01",
                    "end_date": "2025-05",
                }
            ],
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
            "skills": ["Python"],
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
    assert body["skills"] == ["Python"]
    assert body["educations"][0]["entry_type"] == "degree"
    assert body["research"][0]["title"] == "Federated Learning for Edge Devices"


def test_system_prompt_covers_every_schema_field() -> None:
    # schema 改了字段但忘了同步 prompt 时，LLM 就不会输出该字段，这里提前拦住
    schema = ResumeDocument.model_json_schema()
    models = [schema, *schema["$defs"].values()]
    # requires_sponsorship 由程序推导，prompt 里明确禁止输出，不要求出现在 schema 描述里
    fields = {key for model in models for key in model.get("properties", {})} - {
        "requires_sponsorship"
    }

    missing = sorted(key for key in fields if f'"{key}"' not in SYSTEM_PROMPT)
    assert missing == []


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


def _build_minimal_pdf(text: str) -> bytes:
    """手工拼一个最小的单页 PDF，避免为了测试引入新依赖。"""
    content = f"BT /F1 12 Tf 10 100 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >>"
        b" /MediaBox [0 0 200 200] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
    ]

    body = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body += b"%d 0 obj\n%s\nendobj\n" % (index, obj)

    xref_offset = len(body)
    body += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        body += b"%010d 00000 n \n" % offset
    body += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (
        len(objects) + 1,
        xref_offset,
    )
    return bytes(body)


def test_parse_resume_pdf_extracts_structured_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    llm_response = json.dumps({"name": "PDF Candidate", "visa_status": "student_pass"})
    _use_fake_llm(monkeypatch, [llm_response])

    pdf_bytes = _build_minimal_pdf("PDF Candidate")

    response = client.post(
        "/api/v1/resumes/parse-pdf",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "PDF Candidate"


def test_parse_resume_pdf_rejects_non_pdf_upload() -> None:
    response = client.post(
        "/api/v1/resumes/parse-pdf",
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 400


def test_recommendations_rank_matching_job_first() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "candidate": {
                "name": "Jane Tan",
                "visa_status": "student_pass",
                "skills": ["Python", "React", "SQL"],
                "experiences": [
                    {
                        "company": "Acme",
                        "title": "Developer",
                        "start_date": "2023-01",
                        "end_date": "2024-12",
                    }
                ],
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


def test_parsed_resume_feeds_recommendations(monkeypatch: pytest.MonkeyPatch) -> None:
    llm_response = json.dumps(
        {
            "name": "Jane Tan",
            "visa_status": "student_pass",
            "skills": ["Python", "FastAPI", "Docker"],
            "experiences": [
                {
                    "company": "Acme",
                    "title": "Backend Intern",
                    "employment_type": "internship",
                    "start_date": "2024-01",
                    "end_date": "2024-12",
                }
            ],
        }
    )
    _use_fake_llm(monkeypatch, [llm_response])
    parsed = client.post("/api/v1/resumes/parse", json={"text": "Jane Tan resume"}).json()

    job = {
        "title": "Backend Intern",
        "company": "Acme",
        "description": "Build APIs with Python, FastAPI and SQL.",
        "min_experience_years": 1,
    }
    response = client.post(
        "/api/v1/recommendations",
        json={
            "candidate": parsed,
            "jobs": [
                {**job, "job_id": "sponsor", "visa_sponsorship": True},
                {**job, "job_id": "no-sponsor", "visa_sponsorship": False},
            ],
        },
    )

    assert response.status_code == 200
    items = {item["job_id"]: item for item in response.json()["recommendations"]}
    assert items["sponsor"]["eligible"] is True
    assert items["sponsor"]["matched_skills"] == ["fastapi", "python"]
    assert items["sponsor"]["missing_skills"] == ["sql"]
    # student_pass 需要担保，不提供担保的岗位应被硬约束筛掉
    assert items["no-sponsor"]["eligible"] is False


def test_experience_years_merges_overlaps_and_handles_partial_dates() -> None:
    def exp(start: str | None, end: str | None) -> Experience:
        return Experience(company="c", title="t", start_date=start, end_date=end)

    # 1-6 月和 4-12 月重叠，合计 12 个月；缺开始日期的跳过；缺结束日期的只算 1 个月
    overlapping = [exp("2023-01", "2023-06"), exp("2023-04", "2023-12"), exp(None, "2024"), exp("2025-03", None)]
    assert calculate_experience_years(overlapping) == 1.1
    assert calculate_experience_years([exp("2021", "2021")]) == 1.0
    assert calculate_experience_years([exp("2024-01", "present")]) > 0
    assert calculate_experience_years([]) == 0
