from typing import Protocol

from app.core.config import settings


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
