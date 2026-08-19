"""Tests comportementaux via httpx.MockTransport (sans backend réel)."""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from architecto_sdk import ArchitectoClient, AsyncArchitectoClient
from architecto_sdk.errors import ArchitectoAPIError

SSE = (
    'data: {"type": "tool", "name": "search_knowledge_base", "phase": "start"}\n\n'
    'data: {"type": "delta", "text": "Bon"}\n\n'
    'data: {"type": "delta", "text": "jour"}\n\n'
    'data: {"type": "done", "thread_id": "t"}\n\n'
)


def _handler(captured: dict):
    """Renvoie un handler MockTransport qui enregistre la requête reçue."""

    def handle(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        captured["method"] = request.method
        body = request.content
        is_json = "application/json" in request.headers.get("content-type", "")
        captured["json"] = json.loads(body) if body and is_json else None

        path = request.url.path
        if path == "/api/v1/chat":
            return httpx.Response(200, json={"thread_id": "t", "answer": "ok"})
        if path == "/api/v1/chat/stream":
            return httpx.Response(
                200, text=SSE, headers={"content-type": "text/event-stream"}
            )
        if path == "/api/v1/knowledge/ingest":
            return httpx.Response(
                200,
                json={
                    "processed": 1,
                    "skipped_unchanged": 0,
                    "skipped_empty": 0,
                    "chunks": 3,
                    "rejected": [],
                },
            )
        if path == "/api/v1/knowledge/sources":
            if request.method == "DELETE":
                return httpx.Response(204)
            return httpx.Response(
                200, json={"sources": [{"source": "a.md", "title": "A", "chunk_count": 2}]}
            )
        if path == "/api/v1/memory/projects":
            return httpx.Response(
                200, json={"projects": [{"slug": "erp", "name": "ERP", "decision_count": 3}]}
            )
        if path == "/api/v1/memory/decisions":
            return httpx.Response(
                200,
                json={
                    "decisions": [
                        {
                            "id": "1",
                            "title": "pgvector",
                            "status": "Accepted",
                            "context": "c",
                            "decision": "d",
                            "consequences": "cq",
                        }
                    ]
                },
            )
        return httpx.Response(404, json={"detail": "not found"})

    return handle


def _client(captured: dict) -> ArchitectoClient:
    return ArchitectoClient(transport=httpx.MockTransport(_handler(captured)))


def test_chat_envoie_le_champ_project():
    cap: dict = {}
    with _client(cap) as c:
        resp = c.chat("salut", thread_id="t7", project="erp")
    assert resp.answer == "ok"
    assert cap["json"] == {"message": "salut", "thread_id": "t7", "project": "erp"}


def test_stream_chat_parse_les_evenements_sse():
    cap: dict = {}
    with _client(cap) as c:
        events = list(c.stream_chat("salut", project="erp"))
    assert cap["path"] == "/api/v1/chat/stream"
    assert [e.type for e in events] == ["tool", "delta", "delta", "done"]
    assert events[0].name == "search_knowledge_base" and events[0].phase == "start"
    assert "".join(e.text for e in events if e.type == "delta") == "Bonjour"
    assert events[-1].thread_id == "t"


def test_ingest_envoie_un_multipart(tmp_path):
    cap: dict = {}
    f = tmp_path / "doc.md"
    f.write_text("# Titre\ncontenu", encoding="utf-8")
    with _client(cap) as c:
        result = c.ingest([f])
    assert cap["path"] == "/api/v1/knowledge/ingest"
    assert result.processed == 1 and result.chunks == 3


def test_list_sources_parse():
    cap: dict = {}
    with _client(cap) as c:
        sources = c.list_sources()
    assert len(sources) == 1 and sources[0].source == "a.md" and sources[0].chunk_count == 2


def test_delete_source_passe_le_param():
    cap: dict = {}
    with _client(cap) as c:
        c.delete_source("a.md")
    assert cap["method"] == "DELETE"
    assert cap["path"] == "/api/v1/knowledge/sources"
    assert cap["params"] == {"source": "a.md"}


def test_list_projects_et_decisions():
    cap: dict = {}
    with _client(cap) as c:
        projects = c.list_projects()
        decisions = c.list_decisions("erp")
    assert projects[0].slug == "erp" and projects[0].decision_count == 3
    assert cap["params"] == {"project": "erp"}
    assert decisions[0].decision == "d" and decisions[0].title == "pgvector"


def test_erreur_api_levee_avec_le_detail():
    def failing(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "boom interne"})

    client = ArchitectoClient(transport=httpx.MockTransport(failing))
    with client, pytest.raises(ArchitectoAPIError) as exc:
        client.health()
    assert exc.value.status_code == 500
    assert "boom interne" in str(exc.value)


def test_async_chat_et_stream_miroir():
    cap: dict = {}

    async def run():
        async with AsyncArchitectoClient(
            transport=httpx.MockTransport(_handler(cap))
        ) as c:
            resp = await c.chat("salut", project="erp")
            events = [e async for e in c.stream_chat("salut")]
            projects = await c.list_projects()
            return resp, events, projects

    resp, events, projects = asyncio.run(run())
    assert resp.answer == "ok"
    assert [e.type for e in events] == ["tool", "delta", "delta", "done"]
    assert projects[0].slug == "erp"
