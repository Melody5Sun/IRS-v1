from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "IT CareerPilot API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    mind_skills_path: Path = BACKEND_ROOT / "data" / "mind_ontology" / "skills.json"
    mind_concepts_path: Path = BACKEND_ROOT / "data" / "mind_ontology" / "concepts.json"

    # OpenAI 兼容接口用于简历解析
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None

    # 本地岗位职责语义匹配
    responsibility_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    responsibility_similarity_floor: float = 0.35
    responsibility_similarity_full: float = 0.75
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
