import json

import pytest

from architecto.features.chat import router as mod
from architecto.features.chat.router import chat_stream
from architecto.features.chat.schemas import ChatRequest


async def _collect_sse(response) -> list[dict]:
    """Décode les évènements JSON d'un flux SSE (StreamingResponse)."""
    events: list[dict] = []
    async for raw in response.body_iterator:
        chunk = raw.decode() if isinstance(raw, bytes) else raw
        for line in chunk.splitlines():
            if line.startswith("data: "):
                events.append(json.loads(line[len("data: ") :]))
    return events


@pytest.mark.asyncio
async def test_stream_ne_fuit_pas_le_detail_de_l_erreur(monkeypatch, caplog):
    secret = "connexion postgres://user:motdepasse@interne:5432 refusée"

    async def _boom(**_kwargs):
        raise RuntimeError(secret)
        yield  # pragma: no cover — fait de _boom un async generator

    monkeypatch.setattr(mod, "stream_agent", _boom)

    response = await chat_stream(ChatRequest(message="salut", thread_id="t42", project="p"))
    with caplog.at_level("ERROR"):
        events = await _collect_sse(response)

    # Le client ne reçoit qu'un message générique, sans le détail interne.
    assert events == [
        {"type": "error", "message": "Une erreur interne est survenue pendant la génération."}
    ]
    assert secret not in json.dumps(events, ensure_ascii=False)

    # Le détail complet est bien tracé côté serveur.
    assert any(secret in rec.getMessage() or secret in str(rec.exc_info) for rec in caplog.records)
