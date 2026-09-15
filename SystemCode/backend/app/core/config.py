from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 固定指向 SystemCode/backend/.env，不依赖启动时所在目录（从仓库根目录启动也能读到）
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    app_name: str = "IT CareerPilot API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # LLM 供应商尚未确定，先留空占位；三项都配置好之后才能真正调用简历解析的 LLM 接口
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


settings = Settings()
