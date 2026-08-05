"""Initialise la base : extension pgvector + tables SQLAlchemy.

Usage : uv run python scripts/init_db.py
Pour un vrai versionnage de schéma, migrer ensuite vers Alembic.
"""

import asyncio

from sqlalchemy import text

from architecto.core.db import Base, engine
from architecto.features.knowledge.models import Document  # noqa: F401  (enregistre la table)


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    print("Base initialisée (extension vector + tables).")


if __name__ == "__main__":
    asyncio.run(main())
