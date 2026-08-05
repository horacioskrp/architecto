from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings

from architecto.core.config.app import AppSettings
from architecto.core.config.cors import CORSSettings
from architecto.core.config.database import DatabaseSettings
from architecto.core.config.llm import LLMSettings
from architecto.core.config.observability import LangSmithSettings


class Settings(BaseSettings):
    """Configuration racine : composition des sections par domaine.

    Chaque section se charge depuis l'environnement avec son propre préfixe ; on
    n'accède jamais à une valeur en dur mais via `settings.<section>.<champ>`.
    """

    app: AppSettings = Field(default_factory=AppSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instance unique (mémoïsée) — le `.env` n'est lu qu'une fois par process."""
    return Settings()


settings = get_settings()
