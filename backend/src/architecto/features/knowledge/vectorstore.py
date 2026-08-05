from functools import lru_cache

from langchain_postgres import PGVector

from architecto.core.config import settings
from architecto.core.llm import get_embeddings

COLLECTION_NAME = "architecto_knowledge"


@lru_cache
def get_vectorstore() -> PGVector:
    """Store vectoriel pgvector de la base de connaissances (RAG).

    langchain-postgres attend une URL psycopg (driver v3).
    """
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=settings.db.url,
        use_jsonb=True,
    )
