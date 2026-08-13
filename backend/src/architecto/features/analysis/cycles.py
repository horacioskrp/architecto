from __future__ import annotations

from architecto.features.analysis.parser import DependencyGraph


def find_cycles(graph: DependencyGraph) -> list[list[str]]:
    """Cycles de dépendances = composantes fortement connexes de taille > 1 (Tarjan)."""
    index = 0
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        indices[v] = low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in graph.get(v, ()):
            if w not in indices:
                strongconnect(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            if len(component) > 1:
                sccs.append(sorted(component))

    for node in graph:
        if node not in indices:
            strongconnect(node)
    return sorted(sccs)
