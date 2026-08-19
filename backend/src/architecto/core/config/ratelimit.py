from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings


class RateLimitSettings(SectionSettings):
    """Limitation de débit de l'API — préfixe `RATELIMIT_`.

    Défense en profondeur pour une API non authentifiée : fenêtre glissante par
    IP cliente, en mémoire du process. Suffisant pour une app de bureau locale ;
    à remplacer par un store partagé (Redis) si l'API est un jour répliquée.
    """

    model_config = SettingsConfigDict(env_prefix="RATELIMIT_")

    enabled: bool = True
    requests: int = 120  # requêtes autorisées par fenêtre et par client
    window_seconds: int = 60
