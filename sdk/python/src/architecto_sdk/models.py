from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Requête de conversation envoyée à l'agent."""

    message: str = Field(..., min_length=1)
    thread_id: str = "default"
    project: str = ""  # slug du projet (scope la mémoire long terme)


class ChatResponse(BaseModel):
    """Réponse de l'agent."""

    thread_id: str
    answer: str


class ChatStreamEvent(BaseModel):
    """Évènement du flux `POST /chat/stream` (Server-Sent Events).

    `type` vaut `delta` (token dans `text`), `tool` (activité d'outil : `name`
    + `phase` valant `start`/`end`), `done` (fin, `thread_id`) ou `error`
    (`message`). Les champs non pertinents pour un type donné restent `None`.
    """

    type: str
    text: str | None = None
    name: str | None = None
    phase: str | None = None
    thread_id: str | None = None
    message: str | None = None


class HealthStatus(BaseModel):
    """État de santé du service."""

    status: str
    version: str


# --- Base de connaissances (RAG) -------------------------------------------


class SourceOut(BaseModel):
    """Une source ingérée dans la base de connaissances."""

    source: str
    title: str
    chunk_count: int


class IngestResult(BaseModel):
    """Bilan d'une ingestion depuis le client."""

    processed: int
    skipped_unchanged: int
    skipped_empty: int
    chunks: int
    rejected: list[str] = []


# --- Mémoire long terme (projets + décisions) ------------------------------


class ProjectOut(BaseModel):
    """Un projet ayant des décisions enregistrées."""

    slug: str
    name: str
    decision_count: int


class DecisionOut(BaseModel):
    """Une décision d'architecture (ADR)."""

    id: str
    title: str
    status: str
    context: str
    decision: str
    consequences: str
