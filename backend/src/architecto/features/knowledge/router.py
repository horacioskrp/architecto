from fastapi import APIRouter, File, HTTPException, UploadFile

from architecto.core.config import settings
from architecto.features.knowledge.ingestion.adapters import PGVectorIndex, SqlDocumentStore
from architecto.features.knowledge.ingestion.ingestor import Ingestor
from architecto.features.knowledge.ingestion.loaders import LoadedDocument, load_bytes
from architecto.features.knowledge.schemas import IngestResult, SourceOut, SourcesList

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def _make_ingestor() -> Ingestor:
    return Ingestor(SqlDocumentStore(), PGVectorIndex())


@router.post("/ingest", response_model=IngestResult)
async def ingest(files: list[UploadFile] = File(...)) -> IngestResult:  # noqa: B008
    """Ingère des documents téléversés (`.md`, `.txt`, `.pdf`) dans pgvector.

    Idempotent par nom de fichier : réingérer un contenu identique est ignoré,
    un contenu modifié remplace ses anciens chunks.
    """
    limit = settings.knowledge
    if len(files) > limit.max_files:
        raise HTTPException(
            status_code=413,
            detail=f"Trop de fichiers (max {limit.max_files}).",
        )

    docs: list[LoadedDocument] = []
    rejected: list[str] = []
    for upload in files:
        name = upload.filename or "sans-nom"
        data = await upload.read()
        if len(data) > limit.max_upload_bytes:
            rejected.append(f"{name} (trop volumineux)")
            continue
        doc = load_bytes(name, data)
        if doc is None:
            rejected.append(f"{name} (non supporté ou vide)")
            continue
        docs.append(doc)

    summary = _make_ingestor().ingest_documents(docs)
    return IngestResult(
        processed=summary.processed,
        skipped_unchanged=summary.skipped_unchanged,
        skipped_empty=summary.skipped_empty,
        chunks=summary.chunks,
        rejected=rejected,
    )


@router.get("/sources", response_model=SourcesList)
async def list_sources() -> SourcesList:
    """Liste les sources déjà ingérées (les plus récentes d'abord)."""
    infos = SqlDocumentStore().list_all()
    return SourcesList(
        sources=[SourceOut(source=i.source, title=i.title, chunk_count=i.chunk_count) for i in infos]
    )


@router.delete("/sources", status_code=204)
async def delete_source(source: str) -> None:
    """Supprime une source et ses chunks vectoriels."""
    store = SqlDocumentStore()
    chunk_count = store.remove(source)
    if chunk_count is None:
        raise HTTPException(status_code=404, detail="Source inconnue.")
    from architecto.features.knowledge.ingestion.chunking import chunk_id

    PGVectorIndex().delete([chunk_id(source, i) for i in range(chunk_count)])
