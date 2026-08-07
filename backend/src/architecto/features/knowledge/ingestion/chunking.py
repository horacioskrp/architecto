from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from architecto.features.knowledge.ingestion.loaders import LoadedDocument

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


@dataclass
class Chunk:
    """Fragment de document prêt pour l'upsert vectoriel."""

    id: str
    text: str
    metadata: dict[str, Any]


def content_hash(text: str) -> str:
    """Empreinte du contenu (sha256, 64 hex) — détecte l'inchangé à la ré-ingestion."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_key(source: str) -> str:
    """Clé stable dérivée de la source (sha1, 40 hex) — préfixe des ids de chunks."""
    return hashlib.sha1(source.encode("utf-8")).hexdigest()


def chunk_id(source: str, index: int) -> str:
    """Id déterministe d'un chunk : `<sha1(source)>:<index>`."""
    return f"{source_key(source)}:{index}"


def chunk_document(
    doc: LoadedDocument,
    *,
    hash_: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Découpe un document en chunks porteurs de métadonnées (source, titre, index)."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return [
        Chunk(
            id=chunk_id(doc.source, index),
            text=text,
            metadata={
                "source": doc.source,
                "title": doc.title,
                "chunk_index": index,
                "content_hash": hash_,
            },
        )
        for index, text in enumerate(splitter.split_text(doc.text))
    ]
