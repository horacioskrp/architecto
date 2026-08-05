from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings


class DatabaseSettings(SectionSettings):
    """Connexion Postgres/pgvector — préfixe `DB_`.

    L'URL n'est jamais écrite en dur : elle est composée à partir des composants,
    tous surchargables par l'environnement.
    """

    model_config = SettingsConfigDict(env_prefix="DB_")

    driver: str = "postgresql+psycopg"
    host: str = "localhost"
    port: int = 5433
    user: str = "architecto"
    password: SecretStr = SecretStr("architecto")
    name: str = "architecto"

    # Pool / debug
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_pre_ping: bool = True

    @property
    def url(self) -> str:
        """DSN SQLAlchemy async (driver psycopg v3)."""
        return (
            f"{self.driver}://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )
