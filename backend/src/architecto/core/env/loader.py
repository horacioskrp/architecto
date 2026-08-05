"""Résolution et chargement du fichier d'environnement.

Point unique de vérité pour localiser le `.env` : on remonte l'arborescence depuis
ce module jusqu'à trouver le fichier, puis on met le résultat en cache
(`lru_cache`) afin de ne le résoudre qu'une seule fois par process.

Les sections de configuration (`core/config/*`) consomment `env_file()` ; on ne lit
donc jamais un chemin en dur ni ne dépend du répertoire courant.
"""

from functools import lru_cache
from pathlib import Path

#: Nom du fichier d'environnement, surchargé par la variable ENV_FILE si présente.
ENV_FILENAME = "ENV_FILE"
DEFAULT_ENV_FILENAME = ".env"


@lru_cache(maxsize=1)
def find_env_file(filename: str = DEFAULT_ENV_FILENAME) -> Path | None:
    """Remonte l'arborescence depuis ce module et renvoie le premier `.env` trouvé."""
    import os

    override = os.environ.get(ENV_FILENAME)
    if override:
        candidate = Path(override).expanduser().resolve()
        return candidate if candidate.is_file() else None

    start = Path(__file__).resolve().parent
    for directory in (start, *start.parents):
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    return None


@lru_cache(maxsize=1)
def env_file() -> str | None:
    """Chemin absolu du `.env` (str) pour pydantic-settings, ou None si absent."""
    path = find_env_file()
    return str(path) if path else None
