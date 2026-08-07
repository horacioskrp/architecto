from __future__ import annotations

from architecto.features.memory.ports import DecisionIndex, DecisionStore, StoredDecision
from architecto.features.memory.ranking import reciprocal_rank_fusion


def _index_text(*, title: str, context: str, decision: str, consequences: str) -> str:
    return f"{title}\n{context}\n{decision}\n{consequences}"


def save_decision(
    store: DecisionStore,
    index: DecisionIndex,
    *,
    project: str,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    status: str,
) -> str:
    """Persiste la décision (SQL) puis l'indexe (vecteur). Renvoie son id."""
    decision_id = store.add(
        project,
        title=title,
        context=context,
        decision=decision,
        consequences=consequences,
        status=status,
    )
    index.add(
        decision_id,
        project,
        _index_text(title=title, context=context, decision=decision, consequences=consequences),
    )
    return decision_id


def recall_decisions(
    store: DecisionStore,
    index: DecisionIndex,
    *,
    project: str,
    query: str = "",
    k: int = 5,
) -> str:
    """Rappelle les décisions d'un projet.

    Avec `query` : fusionne récence (SQL) et similarité (sémantique) par RRF.
    Sans `query` : liste des plus récentes.
    """
    decisions = store.list_by_project(project)  # récence d'abord
    if not decisions:
        return f"Aucune décision enregistrée pour le projet « {project} »."

    by_id = {d.id: d for d in decisions}
    if query.strip():
        recency = [d.id for d in decisions]
        semantic = index.search(project, query, k=max(k, len(decisions)))
        fused = reciprocal_rank_fusion([semantic, recency])
        ordered_ids = [i for i in fused if i in by_id][:k]
    else:
        ordered_ids = [d.id for d in decisions][:k]

    return _format(project, [by_id[i] for i in ordered_ids])


def _format(project: str, decisions: list[StoredDecision]) -> str:
    lines = [f"Décisions du projet « {project} » :"]
    lines.extend(f"- [{d.status}] {d.title} — {d.decision}" for d in decisions)
    return "\n".join(lines)
