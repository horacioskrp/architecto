from __future__ import annotations

from functools import lru_cache

from langchain_postgres import PGVector
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session

from architecto.core.config import settings
from architecto.core.llm import get_embeddings
from architecto.features.memory.models import ArchitectureDecision, Project
from architecto.features.memory.ports import ProjectSummary, StoredDecision

DECISIONS_COLLECTION = "architecto_decisions"


class SqlDecisionStore:
    """Store SQL des décisions (moteur SQLAlchemy synchrone)."""

    def __init__(self) -> None:
        self._engine = create_engine(settings.db.url, future=True)

    def add(
        self,
        project: str,
        *,
        title: str,
        context: str,
        decision: str,
        consequences: str,
        status: str,
    ) -> str:
        with Session(self._engine) as session:
            proj = session.scalar(select(Project).where(Project.slug == project))
            if proj is None:
                proj = Project(slug=project, name=project)
                session.add(proj)
                session.flush()
            row = ArchitectureDecision(
                project_id=proj.id,
                title=title,
                status=status,
                context=context,
                decision=decision,
                consequences=consequences,
            )
            session.add(row)
            session.commit()
            return str(row.id)

    def list_by_project(self, project: str) -> list[StoredDecision]:
        with Session(self._engine) as session:
            rows = session.scalars(
                select(ArchitectureDecision)
                .join(Project, ArchitectureDecision.project_id == Project.id)
                .where(Project.slug == project)
                .order_by(ArchitectureDecision.created_at.desc(), ArchitectureDecision.id.desc())
            ).all()
            return [
                StoredDecision(
                    id=str(r.id),
                    title=r.title,
                    status=r.status,
                    context=r.context,
                    decision=r.decision,
                    consequences=r.consequences,
                )
                for r in rows
            ]

    def list_projects(self) -> list[ProjectSummary]:
        """Projets ayant au moins une décision, avec le compte, plus récents d'abord."""
        with Session(self._engine) as session:
            rows = session.execute(
                select(
                    Project.slug,
                    Project.name,
                    func.count(ArchitectureDecision.id),
                )
                .join(ArchitectureDecision, ArchitectureDecision.project_id == Project.id)
                .group_by(Project.id)
                .order_by(func.max(ArchitectureDecision.created_at).desc())
            ).all()
            return [ProjectSummary(slug=s, name=n, decision_count=c) for s, n, c in rows]

    def clear(self) -> None:
        with Session(self._engine) as session:
            session.execute(delete(ArchitectureDecision))
            session.execute(delete(Project))
            session.commit()


@lru_cache
def _decisions_vectorstore() -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=DECISIONS_COLLECTION,
        connection=settings.db.url,
        use_jsonb=True,
    )


class PGVectorDecisionIndex:
    """Index vectoriel des décisions (collection dédiée pgvector)."""

    def __init__(self) -> None:
        self._store = _decisions_vectorstore()

    def add(self, decision_id: str, project: str, text: str) -> None:
        self._store.add_texts(
            texts=[text],
            metadatas=[{"project": project, "decision_id": decision_id}],
            ids=[decision_id],
        )

    def search(self, project: str, query: str, k: int) -> list[str]:
        docs = self._store.similarity_search(query, k=k, filter={"project": project})
        return [d.metadata["decision_id"] for d in docs if "decision_id" in d.metadata]

    def clear(self) -> None:
        self._store.delete_collection()
        self._store.create_collection()
