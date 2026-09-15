import re

from app.parsers.skill_lexicon import KNOWN_SKILLS

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
EXPERIENCE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def extract_experience_years(text: str) -> float | None:
    matches = [float(match.group(1)) for match in EXPERIENCE_PATTERN.finditer(text)]
    return max(matches) if matches else None


def extract_skills(text: str) -> list[str]:
    normalized_text = text.lower()
    skills = [
        skill
        for skill in KNOWN_SKILLS
        if re.search(rf"(?<![\w+#.-]){re.escape(skill)}(?![\w+#.-])", normalized_text)
    ]
    return sorted(skills)


def first_non_empty_line(text: str) -> str | None:
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line:
            return clean_line
    return None
