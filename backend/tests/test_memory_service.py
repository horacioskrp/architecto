from architecto.features.memory import service, tools
from architecto.features.memory.ports import StoredDecision


class FakeStore:
    def __init__(self) -> None:
        self.items: list[tuple[str, StoredDecision]] = []
        self._id = 0
        self.last_project: str | None = None

    def add(self, project, *, title, context, decision, consequences, status) -> str:
        self._id += 1
        did = str(self._id)
        self.last_project = project
        self.items.insert(0, (project, StoredDecision(did, title, status, context, decision, consequences)))
        return did

    def list_by_project(self, project):
        return [d for p, d in self.items if p == project]

    def clear(self) -> None:
        self.items.clear()


class FakeIndex:
    def __init__(self, search_result=None) -> None:
        self.added: list[tuple[str, str, str]] = []
        self._search = search_result or []

    def add(self, decision_id, project, text) -> None:
        self.added.append((decision_id, project, text))

    def search(self, project, query, k):
        return list(self._search)

    def clear(self) -> None:
        pass


def _seed(store, index, project="proj"):
    ids = []
    for i in range(1, 4):
        ids.append(
            service.save_decision(
                store, index, project=project,
                title=f"Décision {i}", context="c", decision=f"d{i}", consequences="cq", status="Accepted",
            )
        )
    return ids  # ["1","2","3"], store en récence -> 3,2,1


def test_save_persiste_et_indexe():
    store, index = FakeStore(), FakeIndex()
    did = service.save_decision(
        store, index, project="proj",
        title="Base de données", context="RAG", decision="pgvector", consequences="une base", status="Accepted",
    )
    assert did == "1"
    assert store.last_project == "proj"
    assert index.added == [("1", "proj", "Base de données\nRAG\npgvector\nune base")]


def test_recall_sans_query_liste_recence():
    store, index = FakeStore(), FakeIndex()
    _seed(store, index)
    out = service.recall_decisions(store, index, project="proj")
    # 3 est la plus récente -> apparaît en premier
    assert out.index("Décision 3") < out.index("Décision 2") < out.index("Décision 1")


def test_recall_avec_query_utilise_rrf():
    store = FakeStore()
    # index sémantique remonte d1 en tête (pertinent), alors qu'il est le plus ancien
    index = FakeIndex(search_result=["1"])
    _seed(store, index)
    out = service.recall_decisions(store, index, project="proj", query="pertinence")
    # d1 boosté par le sémantique -> devant d2
    assert out.index("Décision 1") < out.index("Décision 2")


def test_recall_projet_vide():
    store, index = FakeStore(), FakeIndex()
    out = service.recall_decisions(store, index, project="vide")
    assert "Aucune décision" in out


def test_tool_save_utilise_thread_id_si_pas_de_projet(monkeypatch):
    store, index = FakeStore(), FakeIndex()
    monkeypatch.setattr(tools, "make_store", lambda: store)
    monkeypatch.setattr(tools, "make_index", lambda: index)

    msg = tools.save_decision.invoke(
        {"title": "T", "context": "c", "decision": "d", "consequences": "cq"},
        config={"configurable": {"thread_id": "erp-hospitalier"}},
    )
    assert "erp-hospitalier" in msg
    assert store.last_project == "erp-hospitalier"


def test_tool_save_projet_explicite_prioritaire(monkeypatch):
    store, index = FakeStore(), FakeIndex()
    monkeypatch.setattr(tools, "make_store", lambda: store)
    monkeypatch.setattr(tools, "make_index", lambda: index)

    tools.save_decision.invoke(
        {"title": "T", "context": "c", "decision": "d", "consequences": "cq", "project": "banque"},
        config={"configurable": {"thread_id": "ignoré"}},
    )
    assert store.last_project == "banque"
