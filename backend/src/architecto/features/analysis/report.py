from __future__ import annotations

from architecto.features.analysis.layers import LayerViolation


def format_report(
    module_count: int,
    cycles: list[list[str]],
    violations: list[LayerViolation],
) -> str:
    """Rapport Markdown factuel (faits calculés, pas d'interprétation)."""
    lines = [
        "# Analyse de dépendances",
        "",
        f"- Modules analysés : {module_count}",
        "",
        "## Dépendances circulaires",
        "",
    ]
    if cycles:
        lines.extend(f"- cycle : {' -> '.join(cycle)}" for cycle in cycles)
    else:
        lines.append("- aucune")

    lines += ["", "## Violations de couches", ""]
    if violations:
        lines.extend(
            f"- {v.source_layer} -> {v.target_layer} : {v.source} -> {v.target}"
            for v in violations
        )
    else:
        lines.append("- aucune")

    return "\n".join(lines)
