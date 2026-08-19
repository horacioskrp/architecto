from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
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
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_prefix = api_prefix.rstrip("/")
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=dict(headers or {}),
            transport=transport or httpx.HTTPTransport(retries=max_retries),
        )

    def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, f"{self._api_prefix}{path}", **kwargs)
        except httpx.HTTPError as exc:
            raise ArchitectoConnectionError(str(exc)) from exc
        raise_for_status(response)
        return response

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        return self._send(method, path, **kwargs).json()

    def chat(
        self, message: str, thread_id: str = "default", project: str = ""
    ) -> ChatResponse:
        """Envoie un message à l'agent et renvoie sa réponse complète."""
        data = self._request(
            "POST",
            "/chat",
            json={"message": message, "thread_id": thread_id, "project": project},
        )
        return ChatResponse.model_validate(data)

    def stream_chat(
        self, message: str, thread_id: str = "default", project: str = ""
    ) -> Iterator[ChatStreamEvent]:
        """Diffuse la réponse de l'agent évènement par évènement (SSE).

        Produit des `ChatStreamEvent` : `delta` (tokens), `tool` (activité),
        puis `done` ou `error`.
        """
        body = {"message": message, "thread_id": thread_id, "project": project}
        try:
            with self._client.stream(
                "POST", f"{self._api_prefix}/chat/stream", json=body
            ) as response:
                if response.status_code >= 400:
                    response.read()
                    raise_for_status(response)
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        yield ChatStreamEvent.model_validate_json(line[len("data: ") :])
        except httpx.HTTPError as exc:
            raise ArchitectoConnectionError(str(exc)) from exc

    def health(self) -> HealthStatus:
        """Renvoie l'état de santé du service."""
        return HealthStatus.model_validate(self._request("GET", "/health"))

    # --- Base de connaissances ---------------------------------------------

    def ingest(self, files: Sequence[str | Path]) -> IngestResult:
        """Ingère des fichiers (`.md`, `.txt`, `.pdf`) dans la base de connaissances."""
        payload = [("files", (Path(f).name, Path(f).read_bytes())) for f in files]
        data = self._request("POST", "/knowledge/ingest", files=payload)
        return IngestResult.model_validate(data)

    def list_sources(self) -> list[SourceOut]:
        """Liste les sources déjà ingérées (les plus récentes d'abord)."""
        data = self._request("GET", "/knowledge/sources")
        return [SourceOut.model_validate(s) for s in data["sources"]]

    def delete_source(self, source: str) -> None:
        """Supprime une source et ses chunks vectoriels."""
        self._send("DELETE", "/knowledge/sources", params={"source": source})

    # --- Mémoire long terme ------------------------------------------------

    def list_projects(self) -> list[ProjectOut]:
        """Projets ayant des décisions enregistrées (les plus récents d'abord)."""
        data = self._request("GET", "/memory/projects")
        return [ProjectOut.model_validate(p) for p in data["projects"]]

    def list_decisions(self, project: str) -> list[DecisionOut]:
        """Décisions d'architecture (ADR) d'un projet, les plus récentes d'abord."""
        data = self._request("GET", "/memory/decisions", params={"project": project})
        return [DecisionOut.model_validate(d) for d in data["decisions"]]

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ArchitectoClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
