from pydantic import BaseModel


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
    rejected: list[str] = []  # fichiers non supportés / vides / trop volumineux


class SourcesList(BaseModel):
    sources: list[SourceOut]
