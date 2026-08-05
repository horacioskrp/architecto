from fastapi import APIRouter

from architecto.api.v1 import chat, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
