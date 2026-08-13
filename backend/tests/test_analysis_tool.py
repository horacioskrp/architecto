from pathlib import Path

from architecto.features.analysis import parser as parser_mod
from architecto.features.analysis.layers import LayerViolation
from architecto.features.analysis.report import format_report
from architecto.features.analysis.tools import analyze_dependencies


def test_format_report_avec_findings():
    report = format_report(
        3, [["a", "b"]], [LayerViolation("x", "y", "core", "features")]
    )
    assert "Modules analysés : 3" in report
    assert "cycle : a -> b" in report
    assert "core -> features : x -> y" in report


def test_format_report_sans_findings():
    report = format_report(5, [], [])
    assert report.count("- aucune") == 2


def test_analyze_dependencies_source_introuvable():
    out = analyze_dependencies.invoke({"source": "/chemin/inexistant/xyz"})
    assert "Analyse impossible" in out


def test_analyze_dependencies_projet_reel():
    root = Path(parser_mod.__file__).resolve().parents[2]
    out = analyze_dependencies.invoke({"source": str(root)})
    assert "# Analyse de dépendances" in out
    assert "Dépendances circulaires" in out
    # pas de cycle, mais la violation de couche connue apparaît
    assert "architecto.features.chat.router -> architecto.agent.graph" in out
