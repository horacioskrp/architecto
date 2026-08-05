from fastapi import APIRouter

from architecto.features.chat.router import router as chat_router
from architecto.features.health.router import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)
