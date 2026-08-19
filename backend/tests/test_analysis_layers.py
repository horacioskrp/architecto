from pathlib import Path

from architecto.features.analysis import parser as parser_mod
from architecto.features.analysis.layers import (
    find_layer_violations,
    layer_of,
)
from architecto.features.analysis.parser import build_graph


def test_layer_of():
    assert layer_of("architecto.core.config") == "core"
    assert layer_of("architecto.features.knowledge.tools") == "features"
    assert layer_of("architecto") is None


def test_violation_core_vers_features():
    graph = {"architecto.core.x": {"architecto.features.y"}}
    v = find_layer_violations(graph)
    assert len(v) == 1
    assert (v[0].source_layer, v[0].target_layer) == ("core", "features")


def test_direction_valide_pas_de_violation():
    # features -> core (autorisé) et agent -> features (autorisé)
    graph = {
        "architecto.features.k": {"architecto.core.c"},
        "architecto.agent.g": {"architecto.features.k"},
    }
    assert find_layer_violations(graph) == []


def test_meme_couche_autorisee():
    graph = {"architecto.core.a": {"architecto.core.b"}}
    assert find_layer_violations(graph) == []


def test_regles_configurables():
    # règle stricte : features ne peut RIEN importer
    graph = {"architecto.features.k": {"architecto.core.c"}}
    assert find_layer_violations(graph, {"features": set()})


def test_projet_reel_ne_viole_aucune_couche():
    # Garde-fou : le code réel doit respecter la direction des couches.
    # (L'ancienne violation features.chat.router -> agent.graph a été résolue par
    # inversion de dépendance : port ChatAgent + adaptateur injecté dans main.py.)
    root = Path(parser_mod.__file__).resolve().parents[2]
    violations = find_layer_violations(build_graph(root))
    assert violations == [], "\n".join(
        f"{v.source} -> {v.target} ({v.source_layer}->{v.target_layer})" for v in violations
    )
