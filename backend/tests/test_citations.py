from dataclasses import dataclass, field

from architecto.features.knowledge import tools
from architecto.features.knowledge.tools import format_results, search_knowledge_base


@dataclass
class _Doc:
    page_content: str
    metadata: dict = field(default_factory=dict)


def test_format_results_numerote_et_source():
    docs = [
        _Doc("Contenu A", {"title": "ADR 1", "source": "/docs/adr-1.md"}),
        _Doc("Contenu B", {"title": "Patterns", "source": "/docs/patterns.md"}),
    ]
    out = format_results(docs)
    assert "[1] ADR 1 — /docs/adr-1.md" in out
    assert "Contenu A" in out
    assert "[2] Patterns — /docs/patterns.md" in out
    assert "Contenu B" in out


def test_format_results_metadonnees_manquantes():
    out = format_results([_Doc("sans meta")])
    assert "[1] (sans titre) — (source inconnue)" in out
    assert "sans meta" in out


class _FakeStore:
    def __init__(self, docs):
        self._docs = docs

    def similarity_search(self, query, k=4):  # noqa: ARG002
        return self._docs[:k]


def test_search_renvoie_extraits_sources(monkeypatch):
    docs = [_Doc("Extrait", {"title": "Doc", "source": "/docs/x.md"})]
    monkeypatch.setattr(tools, "get_vectorstore", lambda: _FakeStore(docs))

    result = search_knowledge_base.invoke({"query": "microservices"})
    assert "/docs/x.md" in result
    assert "Extrait" in result


def test_search_sans_resultat(monkeypatch):
    monkeypatch.setattr(tools, "get_vectorstore", lambda: _FakeStore([]))
    result = search_knowledge_base.invoke({"query": "rien"})
    assert result == "Aucun document pertinent trouvé."
