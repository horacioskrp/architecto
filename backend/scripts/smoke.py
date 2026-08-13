"""Smoke test e2e : ingestion RAG -> recherche -> un tour de chat.

Valide la chaîne réelle en une commande. La partie RAG (ingestion + recherche)
tourne avec des embeddings locaux (`EMBEDDING_PROVIDER=local`, sans clé). Le tour de
chat nécessite un provider `LLM_*` fonctionnel (avec crédit) ; s'il échoue, le script
le signale proprement sans planter.

Prérequis : `docker compose up -d db` puis `uv run python scripts/init_db.py`.
Usage : uv run python scripts/smoke.py [chemin_docs]
"""

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    docs = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "docs" / "fr"

    print(f"== 1. Ingestion : {docs} ==")
    from architecto.features.knowledge.ingestion.adapters import (
        PGVectorIndex,
        SqlDocumentStore,
    )
    from architecto.features.knowledge.ingestion.ingestor import Ingestor

    summary = Ingestor(SqlDocumentStore(), PGVectorIndex()).ingest_path(docs)
    print(
        f"   traités={summary.processed} inchangés={summary.skipped_unchanged} "
        f"chunks={summary.chunks}"
    )

    print("== 2. Recherche ==")
    from architecto.features.knowledge.tools import search_knowledge_base

    result = search_knowledge_base.invoke(
        {"query": "organisation du backend en features", "k": 1}
    )
    first_line = result.splitlines()[0] if result.strip() else "(vide)"
    print(f"   {first_line}")

    print("== 3. Chat (un tour) ==")
    from architecto.agent.graph import run_agent

    question = "Résume en une phrase comment le backend est organisé. Cite tes sources."
    try:
        answer = asyncio.run(run_agent(question, thread_id="smoke"))
        print(f"   OK : {answer[:200]}")
    except Exception as exc:  # noqa: BLE001  (harnais : on rapporte sans planter)
        print(f"   INDISPONIBLE : {type(exc).__name__}: {str(exc)[:160]}")

    print("\nSmoke terminé.")


if __name__ == "__main__":
    main()
