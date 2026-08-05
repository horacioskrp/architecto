from pydantic_settings import BaseSettings, SettingsConfigDict

from architecto.core.env import env_file


class SectionSettings(BaseSettings):
    """Socle commun à toutes les sections de configuration.

    `model_config` est fusionné avec celui des sous-classes par pydantic v2 :
    chaque section n'a plus qu'à déclarer son `env_prefix`.
    """

    model_config = SettingsConfigDict(
        env_file=env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
