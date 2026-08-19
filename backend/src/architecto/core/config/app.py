from typing import Literal

from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings


class AppSettings(SectionSettings):
    """Paramètres applicatifs — préfixe `APP_`."""

    model_config = SettingsConfigDict(env_prefix="APP_")

    name: str = "Architecto"
    env: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"  # loopback par défaut ; le conteneur force 0.0.0.0
    port: int = 8000

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"
