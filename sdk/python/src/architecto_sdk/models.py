from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Requête de conversation envoyée à l'agent."""

    message: str = Field(..., min_length=1)
    thread_id: str = "default"


class ChatResponse(BaseModel):
    """Réponse de l'agent."""

    thread_id: str
    answer: str


class HealthStatus(BaseModel):
    """État de santé du service."""

    status: str
    version: str
