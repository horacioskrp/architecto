import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from architecto.features.chat.ports import ChatAgent, get_chat_agent
from architecto.features.chat.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    agent: ChatAgent = Depends(get_chat_agent),  # noqa: B008 — dépendance FastAPI
) -> ChatResponse:
    """Point d'entrée de conversation avec l'agent Architecto (réponse complète)."""
    answer = await agent.run(payload.message, payload.thread_id, payload.project)
    return ChatResponse(thread_id=payload.thread_id, answer=answer)


def _sse(event: dict) -> str:
    """Sérialise un évènement au format Server-Sent Events."""
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    agent: ChatAgent = Depends(get_chat_agent),  # noqa: B008 — dépendance FastAPI
) -> StreamingResponse:
    """Diffuse la réponse de l'agent (Server-Sent Events).

    Évènements émis : `{type:"tool", name, phase}` (activité d'outil),
    `{type:"delta", text}` (tokens), puis `{type:"done", thread_id}`,
    ou `{type:"error", message}` en cas d'échec.
    """

    async def event_source() -> AsyncIterator[str]:
        try:
            async for event in agent.stream(
                payload.message, payload.thread_id, payload.project
            ):
                yield _sse(event)
            yield _sse({"type": "done", "thread_id": payload.thread_id})
        except Exception:
            # Le détail de l'erreur (traces, messages du provider, chemins, URLs
            # avec secrets) reste côté serveur ; le client ne reçoit qu'un message
            # générique pour éviter toute fuite d'information (SEC-4).
            logger.exception(
                "Echec du streaming de l'agent (thread_id=%s)", payload.thread_id
            )
            yield _sse(
                {
                    "type": "error",
                    "message": "Une erreur interne est survenue pendant la génération.",
                }
            )

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # désactive le buffering nginx pour un flux immédiat
            "X-Accel-Buffering": "no",
        },
    )
