from typing import Annotated

from pydantic import field_validator
from pydantic_settings import NoDecode, SettingsConfigDict

from architecto.core.config.base import SectionSettings


class CORSSettings(SectionSettings):
    """Politique CORS — préfixe `CORS_`.

    `origins` accepte une liste séparée par des virgules dans l'env
    (ex. `CORS_ORIGINS=http://localhost:5173,https://app.example.com`).
    `NoDecode` désactive le décodage JSON automatique pour laisser le validateur
    faire le split.
    """

    model_config = SettingsConfigDict(env_prefix="CORS_")

    origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    allow_credentials: bool = True

    @field_validator("origins", mode="before")
    @classmethod
    def _split(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value
