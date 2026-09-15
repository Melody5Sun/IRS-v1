from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_parse_resume_extracts_basic_profile() -> None:
    response = client.post(
        "/api/v1/resumes/parse",
        json={
            "text": "Jane Tan\njane@example.com\nPython React SQL\nMaster of Computing\n2 years experience",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Jane Tan"
    assert body["email"] == "jane@example.com"
    assert body["experience_years"] == 2
    assert "python" in body["skills"]


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
