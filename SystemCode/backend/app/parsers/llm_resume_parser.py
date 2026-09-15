import json
from typing import Protocol

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.resume import ResumeDocument

SYSTEM_PROMPT = """你是一个简历解析助手。你会收到一份简历的纯文本内容，需要把它抽取成结构化 JSON。

严格要求：
- 只输出一个 JSON 对象，不要输出任何解释性文字、Markdown 代码块标记或其他内容。
- 字段名和取值范围必须严格遵守下面给出的 schema，不要新增或改名字段。
- 简历里没有写、或者你判断不了的字段，一律留空（字符串填 null，数组填 []），带枚举取值的
  字段（比如 visa_status/employment_type/skills[].level 等）判断不了就填 "not_stated"，
  不要瞎猜或编造简历里没有的信息。
- visa_status 只允许四个取值：
  - singapore_citizen：简历明确写了新加坡公民/Singaporean/Singapore Citizen
  - permanent_resident：简历明确写了新加坡永久居民/PR/Permanent Resident
  - student_pass：简历明确写了持学生准证在读（Student Pass/Student's Pass）
  - not_stated：简历没写，或者写的是需要雇主另外申请工作准证的情况（比如 Employment Pass/S Pass/需要 sponsorship）
- educations 里如果某一条是短期交换/交流项目（exchange/study abroad），entry_type 填
  "exchange"，degree 固定填 "not_applicable"；正常的学位项目 entry_type 填 "degree"。
- 不要输出 requires_sponsorship 字段，这个字段由程序根据 visa_status 自动算出。

JSON schema（字段名、结构、可选枚举值）：
{
  "name": "string | null",
  "email": "string | null",
  "phone": "string | null",
  "location": {"city": "string | null", "country": "string | null"},
  "visa_status": "singapore_citizen | student_pass | permanent_resident | not_stated",
  "desired_position": "string | null",
  "about": "string | null",
  "experiences": [
    {
      "company": "string",
      "title": "string",
      "employment_type": "internship | full_time | part_time | contract | freelance | not_stated",
      "start_date": "string | null",
      "end_date": "string | null",
      "description": "string",
      "country": "string | null"
    }
  ],
  "projects": [
    {"title": "string", "summary": "string", "technologies": ["string"], "role": "string | null"}
  ],
  "skills": [
    {"name": "string", "level": "beginner | intermediate | advanced | expert | not_stated"}
  ],
  "educations": [
    {
      "institution": "string",
      "entry_type": "degree | exchange",
      "degree": "bachelor | master | phd | diploma | not_applicable",
      "major": "string | null",
      "start_date": "string | null",
      "end_date": "string | null",
      "country": "string | null"
    }
  ],
  "certificates": [
    {"name": "string", "issuer": "string | null", "issue_date": "string | null", "expiry_date": "string | null"}
  ],
  "languages": [
    {"name": "string", "level": "native | fluent | intermediate | basic | not_stated"}
  ]
}
"""


class ChatClient(Protocol):
    """LLM 调用的最小接口，测试里可以换成打桩实现。"""

    def complete(self, *, system_prompt: str, user_prompt: str) -> str: ...


class OpenAICompatibleClient:
    """走 OpenAI 兼容的 chat completions 接口。

    供应商由 .env 里的 LLM_BASE_URL/LLM_MODEL/LLM_API_KEY 决定，尚未确定具体接哪家，
    这三项目前都是空占位；真正发起请求时才检查配置是否齐全。
    """

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        if not (settings.llm_api_key and settings.llm_base_url and settings.llm_model):
            raise RuntimeError(
                "LLM 未配置：请在 .env 中设置 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL 后再调用简历解析。"
            )

        # 延迟导入：LLM 供应商未配置时不强制要求已安装/初始化 openai 客户端
        from openai import OpenAI

        client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""


class ResumeParsingError(RuntimeError):
    """LLM 两次尝试后仍未能返回合法的 ResumeDocument JSON。"""


class LLMResumeParser:
    def __init__(self, client: ChatClient | None = None) -> None:
        self.client = client or OpenAICompatibleClient()

    def parse(self, text: str) -> ResumeDocument:
        raw = self.client.complete(system_prompt=SYSTEM_PROMPT, user_prompt=text)
        try:
            return ResumeDocument.model_validate_json(raw)
        except (json.JSONDecodeError, ValidationError) as error:
            return self._retry(text, error)

    def _retry(self, text: str, error: Exception) -> ResumeDocument:
        retry_prompt = (
            f"{text}\n\n"
            f"上一次的输出没有通过校验，错误信息：{error}\n"
            "请重新只输出一个符合 schema 的 JSON 对象。"
        )
        raw = self.client.complete(system_prompt=SYSTEM_PROMPT, user_prompt=retry_prompt)
        try:
            return ResumeDocument.model_validate_json(raw)
        except (json.JSONDecodeError, ValidationError) as retry_error:
            raise ResumeParsingError(
                f"LLM 重试后仍未能返回合法的简历 JSON：{retry_error}"
            ) from retry_error
