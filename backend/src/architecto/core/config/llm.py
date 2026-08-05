from typing import Literal

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings

ChatProvider = Literal["anthropic", "openai", "google", "deepseek"]


class ChatModelSettings(SectionSettings):
    """Modèle de chat, agnostique du provider — préfixe `LLM_`.

    Le provider est résolu à l'exécution par l'adaptateur correspondant
    (voir `core/llm/`). `base_url` sert aux providers OpenAI-compatibles (DeepSeek,
    proxies, self-hosted).
    """

    model_config = SettingsConfigDict(env_prefix="LLM_")

    provider: ChatProvider = "anthropic"
    model: str = "claude-sonnet-5"
    api_key: SecretStr = SecretStr("")
    base_url: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    timeout: int = 60
