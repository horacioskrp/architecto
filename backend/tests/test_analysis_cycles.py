from pathlib import Path

from architecto.features.analysis import parser as parser_mod
from architecto.features.analysis.cycles import find_cycles
from architecto.features.analysis.parser import build_graph


def test_cycle_detecte():
    graph = {"a": {"b"}, "b": {"c"}, "c": {"a"}, "d": {"a"}}
    assert find_cycles(graph) == [["a", "b", "c"]]


def test_pas_de_cycle():
    graph = {"a": {"b"}, "b": {"c"}, "c": set()}
    assert find_cycles(graph) == []


def test_deux_cycles_independants():
    graph = {"a": {"b"}, "b": {"a"}, "x": {"y"}, "y": {"x"}}
    assert find_cycles(graph) == [["a", "b"], ["x", "y"]]


def test_projet_reel_sans_cycle():
    root = Path(parser_mod.__file__).resolve().parents[2]
    assert find_cycles(build_graph(root)) == []  # architecto ne doit pas avoir de cycle
