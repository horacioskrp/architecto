from fastapi import APIRouter

from architecto.features.chat.router import router as chat_router
from architecto.features.health.router import router as health_router
from architecto.features.knowledge.router import router as knowledge_router
from architecto.features.memory.router import router as memory_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(knowledge_router)
api_router.include_router(memory_router)
