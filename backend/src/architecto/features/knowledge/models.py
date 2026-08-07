from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from architecto.core.db import Base


class Document(Base):
    """Registre d'une source ingérée dans la base de connaissances.

    Sert à l'audit et à l'idempotence (*delete-by-source*) : `content_hash` détecte
    l'inchangé, `chunk_count` permet de supprimer les anciens chunks avant réinsertion.
    Les chunks + embeddings eux-mêmes vivent dans pgvector (via langchain-postgres).
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64))
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
