from __future__ import annotations

from dataclasses import dataclass

from architecto.features.analysis.parser import DependencyGraph

# Règles par défaut = archi d'Architecto. Chaque couche -> couches qu'elle PEUT importer
# (les dépendances intra-couche sont toujours autorisées).
DEFAULT_LAYER_RULES: dict[str, set[str]] = {
    "core": set(),
    "features": {"core"},
    "agent": {"features", "core"},
    "api": {"agent", "features", "core"},
}


@dataclass(frozen=True)
class LayerViolation:
    source: str
    target: str
    source_layer: str
    target_layer: str


def layer_of(module: str) -> str | None:
    """Couche d'un module = 2ᵉ segment (`architecto.core.config` -> `core`)."""
    parts = module.split(".")
    return parts[1] if len(parts) >= 2 else None


def find_layer_violations(
    graph: DependencyGraph, rules: dict[str, set[str]] | None = None
) -> list[LayerViolation]:
    """Arêtes qui violent la direction de dépendance autorisée entre couches."""
    rules = DEFAULT_LAYER_RULES if rules is None else rules
    violations: list[LayerViolation] = []
    for source, targets in graph.items():
        src_layer = layer_of(source)
        if src_layer is None or src_layer not in rules:
            continue  # module hors couches connues -> non contraint
        allowed = rules[src_layer]
        for target in targets:
            tgt_layer = layer_of(target)
            if tgt_layer is None or tgt_layer == src_layer:
                continue  # même couche autorisée
            if tgt_layer not in allowed:
                violations.append(LayerViolation(source, target, src_layer, tgt_layer))
    return sorted(violations, key=lambda v: (v.source, v.target))
