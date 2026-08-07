from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from architecto.features.knowledge.ingestion.chunking import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    Chunk,
    chunk_document,
    chunk_id,
    content_hash,
)
from architecto.features.knowledge.ingestion.loaders import iter_files, load_file


@dataclass
class SourceRecord:
    """Trace d'une source déjà ingérée (issue de la table Document)."""

    source: str
    content_hash: str
    chunk_count: int


class DocumentStore(Protocol):
    """Registre des sources (table Document)."""

    def get(self, source: str) -> SourceRecord | None: ...
    def save(self, source: str, title: str, content_hash: str, chunk_count: int) -> None: ...
    def clear(self) -> None: ...


class VectorIndex(Protocol):
    """Index vectoriel (pgvector)."""

    def add(self, chunks: list[Chunk]) -> None: ...
    def delete(self, ids: list[str]) -> None: ...
    def clear(self) -> None: ...


@dataclass
class IngestSummary:
    processed: int = 0  # fichiers (ré)ingérés
    skipped_unchanged: int = 0
    skipped_empty: int = 0
    chunks: int = 0


class Ingestor:
    """Orchestration : load -> hash -> (skip|delete-by-source) -> chunk -> upsert -> trace."""

    def __init__(
        self,
        store: DocumentStore,
        index: VectorIndex,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        self._store = store
        self._index = index
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def ingest_path(self, root: Path, *, reset: bool = False) -> IngestSummary:
        summary = IngestSummary()
        if reset:
            self._index.clear()
            self._store.clear()
        for path in iter_files(root):
            self._ingest_file(path, summary)
        return summary

    def _ingest_file(self, path: Path, summary: IngestSummary) -> None:
        doc = load_file(path)
        if doc is None:  # format non supporté (déjà filtré) ou contenu vide
            summary.skipped_empty += 1
            return

        new_hash = content_hash(doc.text)
        existing = self._store.get(doc.source)
        if existing is not None and existing.content_hash == new_hash:
            summary.skipped_unchanged += 1
            return

        # delete-by-source : purge les anciens chunks avant de réinsérer
        if existing is not None:
            self._index.delete([chunk_id(doc.source, i) for i in range(existing.chunk_count)])

        chunks = chunk_document(
            doc, hash_=new_hash, chunk_size=self._chunk_size, chunk_overlap=self._chunk_overlap
        )
        self._index.add(chunks)
        self._store.save(doc.source, doc.title, new_hash, len(chunks))
        summary.processed += 1
        summary.chunks += len(chunks)
