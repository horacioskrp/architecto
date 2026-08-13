"""Initialise la base : extension pgvector + tables SQLAlchemy.

Usage : uv run python scripts/init_db.py
Script one-shot en moteur synchrone (évite les soucis d'event loop asyncio sous
Windows). Pour un vrai versionnage de schéma, migrer ensuite vers Alembic.
"""

from sqlalchemy import create_engine, text

from architecto.core.config import settings
from architecto.core.db import Base
from architecto.features.knowledge.models import Document  # noqa: F401  (enregistre la table)
from architecto.features.memory.models import (  # noqa: F401  (enregistre les tables)
    ArchitectureDecision,
    Project,
)


def main() -> None:
    engine = create_engine(settings.db.url, future=True)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(conn)
    print("Base initialisée (extension vector + tables).")


if __name__ == "__main__":
    main()
