from pathlib import Path

from app.db.sqlite import DEFAULT_DB_PATH
from app.rule_engine import screen_jobs
from app.schemas.profile import UserProfile
from app.schemas.rules_screening import RulesScreeningResponse


class RulesScreeningService:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DEFAULT_DB_PATH

    def run(self, profile: UserProfile) -> RulesScreeningResponse:
        screened = screen_jobs(profile, self.db_path)
        return RulesScreeningResponse(
            total_jobs=screened.total_jobs,
            passed_count=len(screened.documents),
            rejected_by_rule=screened.rejected_by_rule,
            jobs=screened.documents,
        )
