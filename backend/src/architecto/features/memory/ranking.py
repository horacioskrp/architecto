from __future__ import annotations

from collections.abc import Sequence

RRF_K = 60


def reciprocal_rank_fusion(rankings: Sequence[Sequence[str]], *, k: int = RRF_K) -> list[str]:
    """Fusionne plusieurs listes classées (best-first) par Reciprocal Rank Fusion.

    `score(id) += 1 / (k + rang)` sur chaque liste ; renvoie les ids triés par score
    décroissant. Combine ici récence (SQL) et similarité (sémantique) sans modèle.
    """
    scores: dict[str, float] = {}
    order: list[str] = []
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            if item not in scores:
                scores[item] = 0.0
                order.append(item)
            scores[item] += 1.0 / (k + rank)
    return sorted(order, key=lambda item: scores[item], reverse=True)
