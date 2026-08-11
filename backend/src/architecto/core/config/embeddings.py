from typing import Literal

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings

EmbeddingProvider = Literal["openai", "google", "local"]


class EmbeddingSettings(SectionSettings):
    """Embeddings pour le RAG — préfixe `EMBEDDING_`.

    Découplé du chat : Anthropic/DeepSeek ne fournissent pas d'embeddings ; on peut
    donc utiliser un provider distinct — OpenAI, Gemini, ou `local` (fastembed, sans clé).
    """

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_")

    provider: EmbeddingProvider = "openai"
    model: str = "text-embedding-3-small"
    api_key: SecretStr = SecretStr("")
    base_url: str | None = None
