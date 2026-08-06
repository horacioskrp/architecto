from __future__ import annotations

from typing import Any


class ArchitectoError(Exception):
    """Erreur de base du SDK Architecto."""


class ArchitectoConnectionError(ArchitectoError):
    """Échec de connexion au service (réseau, timeout, DNS…)."""


class ArchitectoAPIError(ArchitectoError):
    """Le service a répondu avec un statut HTTP d'erreur (>= 400)."""

    def __init__(self, status_code: int, message: str, *, body: Any | None = None) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"[{status_code}] {message}")
