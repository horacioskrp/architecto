from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from architecto.core.config import settings
from architecto.features.knowledge.ingestion.chunking import Chunk
from architecto.features.knowledge.ingestion.ingestor import SourceRecord
from architecto.features.knowledge.models import Document
from architecto.features.knowledge.vectorstore import get_vectorstore


@dataclass
class SourceInfo:
    """Vue d'une source ingérée, pour l'affichage/gestion côté client."""

    source: str
    title: str
    chunk_count: int


class SqlDocumentStore:
    """Registre des sources sur la table `documents` (moteur SQLAlchemy synchrone)."""

    def __init__(self) -> None:
        self._engine = create_engine(settings.db.url, future=True)

    def get(self, source: str) -> SourceRecord | None:
        with Session(self._engine) as session:
            doc = session.scalar(select(Document).where(Document.source == source))
            if doc is None:
                return None
            return SourceRecord(doc.source, doc.content_hash, doc.chunk_count)

    def save(self, source: str, title: str, content_hash: str, chunk_count: int) -> None:
        with Session(self._engine) as session:
            doc = session.scalar(select(Document).where(Document.source == source))
            if doc is None:
                session.add(
                    Document(
                        source=source,
                        title=title,
                        content_hash=content_hash,
                        chunk_count=chunk_count,
                    )
                )
            else:
                doc.title = title
                doc.content_hash = content_hash
                doc.chunk_count = chunk_count
            session.commit()

    def clear(self) -> None:
        with Session(self._engine) as session:
            session.execute(delete(Document))
            session.commit()

    def list_all(self) -> list[SourceInfo]:
        """Toutes les sources ingérées, les plus récentes d'abord."""
        with Session(self._engine) as session:
            docs = session.scalars(
                select(Document).order_by(Document.updated_at.desc())
            ).all()
            return [SourceInfo(d.source, d.title, d.chunk_count) for d in docs]

    def remove(self, source: str) -> int | None:
        """Supprime la trace d'une source. Renvoie son `chunk_count`, ou None si absente."""
        with Session(self._engine) as session:
            doc = session.scalar(select(Document).where(Document.source == source))
            if doc is None:
                return None
            count = doc.chunk_count
            session.delete(doc)
            session.commit()
            return count


class PGVectorIndex:
    """Index vectoriel adossé à pgvector (via langchain-postgres)."""

    def __init__(self) -> None:
        self._store = get_vectorstore()

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        self._store.add_texts(
            texts=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
            ids=[c.id for c in chunks],
        )

    def delete(self, ids: list[str]) -> None:
        if ids:
            self._store.delete(ids=ids)

    def clear(self) -> None:
        self._store.delete_collection()
        self._store.create_collection()
