"""Ingestion de documents dans la base de connaissances (pgvector).

Usage :
    uv run python scripts/ingest.py <fichier|dossier> [--reset]
                                    [--chunk-size N] [--chunk-overlap N]

Nécessite la base démarrée et une clé d'embeddings configurée (EMBEDDING_API_KEY).
"""

import argparse
import time
from pathlib import Path

from architecto.features.knowledge.ingestion.adapters import PGVectorIndex, SqlDocumentStore
from architecto.features.knowledge.ingestion.chunking import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
)
from architecto.features.knowledge.ingestion.ingestor import Ingestor


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestion RAG dans pgvector.")
    parser.add_argument("path", type=Path, help="Fichier ou dossier à ingérer")
    parser.add_argument(
        "--reset", action="store_true", help="Purge la collection et le registre avant ingestion"
    )
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    args = parser.parse_args()

    if not args.path.exists():
        parser.error(f"chemin introuvable : {args.path}")

    ingestor = Ingestor(
        SqlDocumentStore(),
        PGVectorIndex(),
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    start = time.perf_counter()
    summary = ingestor.ingest_path(args.path, reset=args.reset)
    elapsed = time.perf_counter() - start

    print(f"Ingestion terminée en {elapsed:.1f}s")
    print(f"  fichiers traités    : {summary.processed}")
    print(f"  inchangés (ignorés) : {summary.skipped_unchanged}")
    print(f"  vides (ignorés)     : {summary.skipped_empty}")
    print(f"  chunks créés        : {summary.chunks}")


if __name__ == "__main__":
    main()
