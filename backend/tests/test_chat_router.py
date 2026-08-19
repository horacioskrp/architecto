import json

import pytest

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


class _BoomAgent:
    """Faux ChatAgent dont le flux échoue, pour vérifier le confinement d'erreur."""

    def __init__(self, secret: str) -> None:
        self._secret = secret

    async def run(self, *_a: str) -> str:  # pragma: no cover — non utilisé ici
        return ""

    async def stream(self, *_a: str):
        raise RuntimeError(self._secret)
        yield  # pragma: no cover — fait de stream un async generator


@pytest.mark.asyncio
async def test_stream_ne_fuit_pas_le_detail_de_l_erreur(caplog):
    secret = "connexion postgres://user:motdepasse@interne:5432 refusée"

    response = await chat_stream(
        ChatRequest(message="salut", thread_id="t42", project="p"),
        agent=_BoomAgent(secret),
    )
    with caplog.at_level("ERROR"):
        events = await _collect_sse(response)

    # Le client ne reçoit qu'un message générique, sans le détail interne.
    assert events == [
        {"type": "error", "message": "Une erreur interne est survenue pendant la génération."}
    ]
    assert secret not in json.dumps(events, ensure_ascii=False)

    # Le détail complet est bien tracé côté serveur.
    assert any(secret in rec.getMessage() or secret in str(rec.exc_info) for rec in caplog.records)
