from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings


class LLMSettings(SectionSettings):
    """Modèle de langage et embeddings — préfixe `LLM_`."""

    model_config = SettingsConfigDict(env_prefix="LLM_")

    provider: str = "openai"
    api_key: SecretStr = SecretStr("")
    model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.2
    max_tokens: int | None = None
    timeout: int = 60
