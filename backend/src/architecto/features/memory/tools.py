from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from architecto.features.memory import service
from architecto.features.memory.adapters import PGVectorDecisionIndex, SqlDecisionStore
from architecto.features.memory.identity import resolve_project


def make_store() -> SqlDecisionStore:
    return SqlDecisionStore()


def make_index() -> PGVectorDecisionIndex:
    return PGVectorDecisionIndex()


def _configurable(config: RunnableConfig | None, key: str) -> str | None:
    if not config:
        return None
    return (config.get("configurable") or {}).get(key)


def _resolve(project: str, config: RunnableConfig | None) -> str:
    """Projet effectif : arg outil > `project` de la config (front) > thread_id."""
    return resolve_project(
        project or _configurable(config, "project"),
        _configurable(config, "thread_id"),
    )


@tool
def save_decision(
    title: str,
    context: str,
    decision: str,
    consequences: str,
    status: str = "Proposed",
    project: str = "",
    config: RunnableConfig = None,  # injecté par LangChain (exclu du schéma LLM)
) -> str:
    """Enregistre une décision d'architecture dans la mémoire long terme du projet.

    À utiliser dès qu'une décision structurante est prise (choix de stack, découpage,
    sécurité...). `project` : slug du projet (sinon rattaché à la conversation courante).
    """
    project_slug = _resolve(project, config)
    decision_id = service.save_decision(
        make_store(),
        make_index(),
        project=project_slug,
        title=title,
        context=context,
        decision=decision,
        consequences=consequences,
        status=status,
    )
    return f"Décision enregistrée (projet « {project_slug} », id {decision_id})."


@tool
def recall_decisions(
    query: str = "",
    project: str = "",
    k: int = 5,
    config: RunnableConfig = None,  # injecté par LangChain (exclu du schéma LLM)
) -> str:
    """Rappelle les décisions d'architecture déjà prises pour le projet.

    Avec `query`, classe par pertinence (récence + similarité) ; sinon liste les plus
    récentes. `project` : slug (sinon conversation courante).
    """
    project_slug = _resolve(project, config)
    return service.recall_decisions(
        make_store(), make_index(), project=project_slug, query=query, k=k
    )
