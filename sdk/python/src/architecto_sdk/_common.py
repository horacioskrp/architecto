from __future__ import annotations

import httpx

from architecto_sdk.errors import ArchitectoAPIError

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_API_PREFIX = "/api/v1"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2


def raise_for_status(response: httpx.Response) -> None:
    """Lève ArchitectoAPIError si la réponse a un statut >= 400."""
    if response.status_code < 400:
        return
    try:
        body: object = response.json()
    except ValueError:
        body = response.text
    if isinstance(body, dict) and "detail" in body:
        message = str(body["detail"])
    else:
        message = response.reason_phrase or "Erreur API"
    raise ArchitectoAPIError(response.status_code, message, body=body)
