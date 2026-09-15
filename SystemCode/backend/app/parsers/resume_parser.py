from app.parsers.text_parser import (
    extract_email,
    extract_experience_years,
    extract_phone,
    extract_skills,
    first_non_empty_line,
)
from app.schemas.resume import ResumeProfile


class ResumeParser:
    def parse(self, text: str) -> ResumeProfile:
        return ResumeProfile(
            name=first_non_empty_line(text),
            email=extract_email(text),
            phone=extract_phone(text),
            skills=extract_skills(text),
            education=self._extract_education(text),
            experience_years=extract_experience_years(text),
            work_authorization=self._extract_work_authorization(text),
        )

    def _extract_education(self, text: str) -> list[str]:
        education_keywords = ("bachelor", "master", "phd", "degree", "diploma")
        return [
            line.strip()
            for line in text.splitlines()
            if any(keyword in line.lower() for keyword in education_keywords)
        ]

    def _extract_work_authorization(self, text: str) -> str | None:
        lower_text = text.lower()
        if "citizen" in lower_text:
            return "citizen"
        if "permanent resident" in lower_text or "pr" in lower_text:
            return "permanent_resident"
        if "student pass" in lower_text:
            return "student_pass"
        if "need sponsorship" in lower_text or "require sponsorship" in lower_text:
            return "requires_sponsorship"
        return None
