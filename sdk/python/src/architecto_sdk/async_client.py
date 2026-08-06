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


class AsyncArchitectoClient:
    """Client asynchrone pour l'API Architecto.

    Exemple :
        async with AsyncArchitectoClient("http://localhost:8000") as client:
            print((await client.health()).version)
            print((await client.chat("Propose une archi hexagonale")).answer)
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
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=dict(headers or {}),
            transport=httpx.AsyncHTTPTransport(retries=max_retries),
        )

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = await self._client.request(method, f"{self._api_prefix}{path}", **kwargs)
        except httpx.HTTPError as exc:
            raise ArchitectoConnectionError(str(exc)) from exc
        raise_for_status(response)
        return response.json()

    async def chat(self, message: str, thread_id: str = "default") -> ChatResponse:
        """Envoie un message à l'agent et renvoie sa réponse."""
        data = await self._request(
            "POST", "/chat", json={"message": message, "thread_id": thread_id}
        )
        return ChatResponse.model_validate(data)

    async def health(self) -> HealthStatus:
        """Renvoie l'état de santé du service."""
        return HealthStatus.model_validate(await self._request("GET", "/health"))

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncArchitectoClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()
