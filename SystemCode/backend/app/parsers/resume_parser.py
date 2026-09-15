from app.parsers.llm_resume_parser import LLMResumeParser
from app.schemas.resume import ResumeDocument


class ResumeParser:
    def __init__(self, llm_parser: LLMResumeParser | None = None) -> None:
        self.llm_parser = llm_parser or LLMResumeParser()

    def parse(self, text: str) -> ResumeDocument:
        return self.llm_parser.parse(text)
