import pytest
from fastapi.testclient import TestClient
from job_db import API_JOBS, make_file_db

from app.api.v1.routes import ranking as ranking_route
from app.api.v1.routes import rules_screening as rules_screening_route
from app.main import app
from app.services.ranking_service import RankingService
from app.services.rules_screening_service import RulesScreeningService
from app.services.skill_match_service import SkillMatchService


@pytest.fixture
def screening_client(monkeypatch: pytest.MonkeyPatch, tmp_path) -> TestClient:
    """把 rules-screening / ranking 两个接口指向 tmp_path 里的库（API_JOBS），不碰被 git 跟踪的 careerpilot.db。"""
    rules_service = RulesScreeningService(make_file_db(tmp_path, *API_JOBS))
    monkeypatch.setattr(rules_screening_route, "rules_screening_service", rules_service)
    monkeypatch.setattr(ranking_route, "ranking_service", RankingService(rules_service, SkillMatchService()))
    return TestClient(app)
