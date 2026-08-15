from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class StoredDecision:
    """Décision telle que renvoyée par le store (id sous forme de chaîne)."""

    id: str
    title: str
    status: str
    context: str
    decision: str
    consequences: str


@dataclass
class ProjectSummary:
    """Projet + nombre de décisions (pour l'affichage côté client)."""

    slug: str
    name: str
    decision_count: int


class DecisionStore(Protocol):
    """Persistance des décisions (source de vérité SQL)."""

    def add(
        self,
        project: str,
        *,
        title: str,
        context: str,
        decision: str,
        consequences: str,
        status: str,
    ) -> str: ...

    def list_by_project(self, project: str) -> list[StoredDecision]: ...

    def clear(self) -> None: ...


class DecisionIndex(Protocol):
    """Index vectoriel des décisions (recherche sémantique)."""

    def add(self, decision_id: str, project: str, text: str) -> None: ...

    def search(self, project: str, query: str, k: int) -> list[str]: ...

    def clear(self) -> None: ...
