from fastapi import APIRouter

from architecto.agent.graph import run_agent
from architecto.features.chat.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Point d'entrée de conversation avec l'agent Architecto."""
    answer = await run_agent(
        message=payload.message, thread_id=payload.thread_id, project=payload.project
    )
    return ChatResponse(thread_id=payload.thread_id, answer=answer)
