from app.parsers.job_parser import JobParser
from app.schemas.job import JobAnalysis, JobAnalysisRequest


class JobService:
    def __init__(self, parser: JobParser | None = None) -> None:
        self.parser = parser or JobParser()

    def analyze(self, request: JobAnalysisRequest) -> JobAnalysis:
        return self.parser.analyze(request)
