from typing import Literal

from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings

CheckpointerKind = Literal["memory", "postgres"]


class AgentSettings(SectionSettings):
    """Comportement de l'agent — préfixe `AGENT_`.

    `checkpointer` choisit la persistance des threads LangGraph :
    - `memory` : en mémoire (dev/tests, threads perdus au redémarrage) ;
    - `postgres` : durable via `AsyncPostgresSaver` (recommandé en production).
    """

    model_config = SettingsConfigDict(env_prefix="AGENT_")

    checkpointer: CheckpointerKind = "memory"
