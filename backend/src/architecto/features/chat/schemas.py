from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message de l'utilisateur")
    thread_id: str = Field("default", description="Identifiant de conversation (mémoire)")
    project: str = Field("", description="Slug du projet (scope la mémoire long terme)")


class ChatResponse(BaseModel):
    thread_id: str
    answer: str
