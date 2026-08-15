from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from architecto.core.config import settings


@asynccontextmanager
async def postgres_checkpointer() -> AsyncIterator[object]:
    """Ouvre un `AsyncPostgresSaver` (persistance durable des threads).

    Contexte async : crée la connexion, applique le schéma (`setup`), puis
    libère la connexion à la sortie. Import paresseux pour ne pas alourdir le
    démarrage quand le checkpointer en mémoire est utilisé.
    """
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

    async with AsyncPostgresSaver.from_conn_string(settings.db.psycopg_dsn) as saver:
        await saver.setup()
        yield saver
