from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings


class LangSmithSettings(SectionSettings):
    """Traçabilité / observabilité LangSmith — préfixe `LANGSMITH_`."""

    model_config = SettingsConfigDict(env_prefix="LANGSMITH_")

    tracing: bool = False
    api_key: SecretStr = SecretStr("")
    project: str = "architecto"
    endpoint: str = "https://api.smith.langchain.com"

    @property
    def enabled(self) -> bool:
        return self.tracing and bool(self.api_key.get_secret_value())
