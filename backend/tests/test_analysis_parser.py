from pathlib import Path

from architecto.features.analysis import parser as parser_mod
from architecto.features.analysis.parser import build_graph


def _make_pkg(tmp_path: Path) -> Path:
    root = tmp_path / "src"
    proj = root / "proj"
    proj.mkdir(parents=True)
    (proj / "__init__.py").write_text("", encoding="utf-8")
    (proj / "a.py").write_text("import proj.b\nimport os\n", encoding="utf-8")
    (proj / "b.py").write_text("from . import c\n", encoding="utf-8")
    (proj / "c.py").write_text("from proj.a import x\n", encoding="utf-8")  # cycle a->b->c->a
    return proj


def test_build_graph_synthetique(tmp_path: Path):
    graph = build_graph(_make_pkg(tmp_path))
    assert graph["proj.a"] == {"proj.b"}
    assert graph["proj.b"] == {"proj.c"}  # import relatif résolu
    assert graph["proj.c"] == {"proj.a"}
    assert graph["proj"] == set()  # __init__ vide


def test_imports_externes_ignores(tmp_path: Path):
    graph = build_graph(_make_pkg(tmp_path))
    # 'os' (externe) n'apparaît nulle part
    assert all(all(dep.startswith("proj") for dep in deps) for deps in graph.values())


def test_build_graph_projet_reel():
    # parser.py -> features/analysis/parser.py ; parents[2] == package "architecto"
    root = Path(parser_mod.__file__).resolve().parents[2]
    graph = build_graph(root)
    assert "architecto.agent.tools" in graph
    assert any(
        dep.startswith("architecto.features") for dep in graph["architecto.agent.tools"]
    )
