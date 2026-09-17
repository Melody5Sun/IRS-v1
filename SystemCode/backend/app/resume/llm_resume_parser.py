import json

from pydantic import ValidationError

from app.schemas.resume import ParsedResume
from app.services.openai_client_service import ChatClient, OpenAICompatibleClient

# prompt 用英文写：输出必须是英文，中文指令容易让模型把中文带进 JSON 值里
SYSTEM_PROMPT = """You are a resume parser. Convert the resume text into ONE JSON object following the schema below. Output raw JSON only: no markdown, no comments, no extra text.

Rules:
1. No fabrication: use only what the resume states. If absent or unclear: "string|null" -> null, list -> [], enum -> "not_stated" (or "not_applicable" where listed), required "string" -> "".
2. Be complete: read every section; keep every entry and every bullet point (tools, numbers, outcomes) without merging or shortening. Each item goes in exactly one section.
3. English only: translate non-English text faithfully; use an organization's official English name, otherwise romanize. Keep emails, phones and URLs unchanged.
4. Dates: "YYYY-MM", or "YYYY" if only the year is given. Ongoing -> end_date "present"; expected graduation -> that date.
5. Use only schema keys. Ignore content with no matching field (awards, GPA, coursework, activities, hobbies).

Schema (// explains the field):
{
  "name": "string|null", "email": "string|null", "phone": "string|null",
  "about": "string|null",  // the resume's own summary/objective; never write one
  "experiences": [{  // employment: internship, full-time, part-time, contract, freelance
    "company": "string", "title": "string",
    "employment_type": "internship|full_time|part_time|contract|freelance|not_stated",  // explicit wording only; a plain job title -> not_stated
    "start_date": "string|null", "end_date": "string|null",
    "description": "string",  // all bullet points, joined with "\\n"
    "country": "string|null"  // country of the stated work location
  }],
  "projects": [{  // personal, course, hackathon, open-source
    "title": "string",
    "summary": "string",  // what was built, how, results; all bullet points
    "technologies": ["string"],  // named for this project
    "role": "string|null"
  }],
  "research": [{  // academic research: thesis, lab/supervised research, research assistantship, publications
    "title": "string",  // topic or paper title
    "institution": "string|null",  // university, lab or institute
    "summary": "string",  // problem, methods, results; publication venue if any
    "start_date": "string|null", "end_date": "string|null"
  }],
  "skills": ["string"],  // one skill per item (split "Python/Java"); from the skills section and technologies named elsewhere; no duplicates
  "educations": [{  // diploma or above, plus exchange programmes; skip secondary school
    "institution": "string",
    "entry_type": "degree|exchange",  // exchange = exchange/study abroad without a degree
    "degree": "bachelor|master|phd|diploma|not_applicable",  // exchange -> not_applicable
    "major": "string|null",
    "start_date": "string|null", "end_date": "string|null",
    "country": "string|null"
  }],
  "certificates": [{"name": "string", "issuer": "string|null", "issue_date": "string|null", "expiry_date": "string|null"}],  // professional certifications
  "languages": ["string"]  // human languages only, one per item; programming languages go in skills
}
"""


class ResumeParsingError(RuntimeError):
    """LLM 两次尝试后仍未能返回合法的 ParsedResume JSON。"""


class LLMResumeParser:
    def __init__(self, client: ChatClient | None = None) -> None:
        self.client = client or OpenAICompatibleClient()

    def parse(self, text: str) -> ParsedResume:
        raw = self.client.complete(system_prompt=SYSTEM_PROMPT, user_prompt=text)
        try:
            return ParsedResume.model_validate_json(raw)
        except (json.JSONDecodeError, ValidationError) as error:
            return self._retry(text, error)

    def _retry(self, text: str, error: Exception) -> ParsedResume:
        retry_prompt = (
            f"{text}\n\n"
            f"上一次的输出没有通过校验，错误信息：{error}\n"
            "请重新只输出一个符合 schema 的 JSON 对象。"
        )
        raw = self.client.complete(system_prompt=SYSTEM_PROMPT, user_prompt=retry_prompt)
        try:
            return ParsedResume.model_validate_json(raw)
        except (json.JSONDecodeError, ValidationError) as retry_error:
            raise ResumeParsingError(
                f"LLM 重试后仍未能返回合法的简历 JSON：{retry_error}"
            ) from retry_error
