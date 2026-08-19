from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from pathlib import Path
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
from architecto_sdk.models import (
    ChatResponse,
    ChatStreamEvent,
    DecisionOut,
    HealthStatus,
    IngestResult,
    ProjectOut,
    SourceOut,
)


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
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_prefix = api_prefix.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=dict(headers or {}),
            transport=transport or httpx.AsyncHTTPTransport(retries=max_retries),
        )

    async def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = await self._client.request(method, f"{self._api_prefix}{path}", **kwargs)
        except httpx.HTTPError as exc:
            raise ArchitectoConnectionError(str(exc)) from exc
        raise_for_status(response)
        return response

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        return (await self._send(method, path, **kwargs)).json()

    async def chat(
        self, message: str, thread_id: str = "default", project: str = ""
    ) -> ChatResponse:
        """Envoie un message à l'agent et renvoie sa réponse complète."""
        data = await self._request(
            "POST",
            "/chat",
            json={"message": message, "thread_id": thread_id, "project": project},
        )
        return ChatResponse.model_validate(data)

    async def stream_chat(
        self, message: str, thread_id: str = "default", project: str = ""
    ) -> AsyncIterator[ChatStreamEvent]:
        """Diffuse la réponse de l'agent évènement par évènement (SSE).

        Produit des `ChatStreamEvent` : `delta` (tokens), `tool` (activité),
        puis `done` ou `error`.
        """
        body = {"message": message, "thread_id": thread_id, "project": project}
        try:
            async with self._client.stream(
                "POST", f"{self._api_prefix}/chat/stream", json=body
            ) as response:
                if response.status_code >= 400:
                    await response.aread()
                    raise_for_status(response)
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield ChatStreamEvent.model_validate_json(line[len("data: ") :])
        except httpx.HTTPError as exc:
            raise ArchitectoConnectionError(str(exc)) from exc

    async def health(self) -> HealthStatus:
        """Renvoie l'état de santé du service."""
        return HealthStatus.model_validate(await self._request("GET", "/health"))

    # --- Base de connaissances ---------------------------------------------

    async def ingest(self, files: Sequence[str | Path]) -> IngestResult:
        """Ingère des fichiers (`.md`, `.txt`, `.pdf`) dans la base de connaissances."""
        payload = [("files", (Path(f).name, Path(f).read_bytes())) for f in files]
        data = await self._request("POST", "/knowledge/ingest", files=payload)
        return IngestResult.model_validate(data)

    async def list_sources(self) -> list[SourceOut]:
        """Liste les sources déjà ingérées (les plus récentes d'abord)."""
        data = await self._request("GET", "/knowledge/sources")
        return [SourceOut.model_validate(s) for s in data["sources"]]

    async def delete_source(self, source: str) -> None:
        """Supprime une source et ses chunks vectoriels."""
        await self._send("DELETE", "/knowledge/sources", params={"source": source})

    # --- Mémoire long terme ------------------------------------------------

    async def list_projects(self) -> list[ProjectOut]:
        """Projets ayant des décisions enregistrées (les plus récents d'abord)."""
        data = await self._request("GET", "/memory/projects")
        return [ProjectOut.model_validate(p) for p in data["projects"]]

    async def list_decisions(self, project: str) -> list[DecisionOut]:
        """Décisions d'architecture (ADR) d'un projet, les plus récentes d'abord."""
        data = await self._request("GET", "/memory/decisions", params={"project": project})
        return [DecisionOut.model_validate(d) for d in data["decisions"]]

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncArchitectoClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()
