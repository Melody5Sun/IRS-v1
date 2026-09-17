from app.resume.llm_resume_parser import LLMResumeParser
from app.schemas.resume import ParsedResume


class ResumeParser:
    def __init__(self, llm_parser: LLMResumeParser | None = None) -> None:
        self.llm_parser = llm_parser or LLMResumeParser()

    def parse(self, text: str) -> ParsedResume:
        return self.llm_parser.parse(text)
