from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings

from architecto.core.config.agent import AgentSettings
from architecto.core.config.app import AppSettings
from architecto.core.config.cors import CORSSettings
from architecto.core.config.database import DatabaseSettings
from architecto.core.config.embeddings import EmbeddingSettings
from architecto.core.config.knowledge import KnowledgeSettings
from architecto.core.config.llm import ChatModelSettings
from architecto.core.config.observability import LangSmithSettings


class Settings(BaseSettings):
    """Configuration racine : composition des sections par domaine.

    Chaque section se charge depuis l'environnement avec son propre préfixe ; on
    n'accède jamais à une valeur en dur mais via `settings.<section>.<champ>`.
    """

    app: AppSettings = Field(default_factory=AppSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: ChatModelSettings = Field(default_factory=ChatModelSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    knowledge: KnowledgeSettings = Field(default_factory=KnowledgeSettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instance unique (mémoïsée) — le `.env` n'est lu qu'une fois par process."""
    return Settings()


settings = get_settings()
