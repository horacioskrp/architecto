from __future__ import annotations

import subprocess

from langchain_core.tools import tool

from architecto.features.analysis.cycles import find_cycles
from architecto.features.analysis.layers import find_layer_violations
from architecto.features.analysis.parser import build_graph
from architecto.features.analysis.report import format_report
from architecto.features.analysis.source import resolve_source


@tool
def analyze_dependencies(source: str) -> str:
    """Analyse statique des dépendances d'un projet Python (chemin local ou dépôt GitHub).

    Détecte les **dépendances circulaires** et les **violations de couches**
    (core < features < agent < api). N'appelle **aucun** LLM : les findings sont des
    faits calculés à partir du code.
    """
    try:
        with resolve_source(source) as root:
            graph = build_graph(root)
    except (FileNotFoundError, OSError) as exc:
        return f"Analyse impossible : {exc}"
    except subprocess.SubprocessError as exc:
        return f"Clone GitHub échoué : {exc}"

    return format_report(len(graph), find_cycles(graph), find_layer_violations(graph))
