from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from architecto_sdk._common import (
    DEFAULT_API_PREFIX,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    raise_for_status,
)
from architecto_sdk.errors import ArchitectoConnectionError
from architecto_sdk.models import ChatResponse, HealthStatus


class ArchitectoClient:
    """Client synchrone pour l'API Architecto.

    Exemple :
        with ArchitectoClient("http://localhost:8000") as client:
            print(client.health().version)
            print(client.chat("Propose une archi pour une API de réservation").answer)
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        api_prefix: str = DEFAULT_API_PREFIX,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self._api_prefix = api_prefix.rstrip("/")
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=dict(headers or {}),
            transport=httpx.HTTPTransport(retries=max_retries),
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, f"{self._api_prefix}{path}", **kwargs)
        except httpx.HTTPError as exc:
            raise ArchitectoConnectionError(str(exc)) from exc
        raise_for_status(response)
        return response.json()

    def chat(self, message: str, thread_id: str = "default") -> ChatResponse:
        """Envoie un message à l'agent et renvoie sa réponse."""
        data = self._request("POST", "/chat", json={"message": message, "thread_id": thread_id})
        return ChatResponse.model_validate(data)

    def health(self) -> HealthStatus:
        """Renvoie l'état de santé du service."""
        return HealthStatus.model_validate(self._request("GET", "/health"))

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ArchitectoClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
