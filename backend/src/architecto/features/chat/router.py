import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from architecto.agent.graph import run_agent, stream_agent
from architecto.features.chat.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Point d'entrée de conversation avec l'agent Architecto (réponse complète)."""
    answer = await run_agent(
        message=payload.message, thread_id=payload.thread_id, project=payload.project
    )
    return ChatResponse(thread_id=payload.thread_id, answer=answer)


def _sse(event: dict) -> str:
    """Sérialise un évènement au format Server-Sent Events."""
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
    """Diffuse la réponse de l'agent (Server-Sent Events).

    Évènements émis : `{type:"tool", name, phase}` (activité d'outil),
    `{type:"delta", text}` (tokens), puis `{type:"done", thread_id}`,
    ou `{type:"error", message}` en cas d'échec.
    """

    async def event_source() -> AsyncIterator[str]:
        try:
            async for event in stream_agent(
                message=payload.message,
                thread_id=payload.thread_id,
                project=payload.project,
            ):
                yield _sse(event)
            yield _sse({"type": "done", "thread_id": payload.thread_id})
        except Exception as exc:  # noqa: BLE001 — surface l'erreur au client
            yield _sse({"type": "error", "message": str(exc)})

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
