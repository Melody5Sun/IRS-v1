from app.parsers.resume_parser import ResumeParser
from app.schemas.resume import ResumeProfile


class ResumeService:
    def __init__(self, parser: ResumeParser | None = None) -> None:
        self.parser = parser or ResumeParser()

    def parse_text(self, text: str) -> ResumeProfile:
        return self.parser.parse(text)
