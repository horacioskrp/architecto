from architecto.agent import graph
from architecto.agent.graph import build_graph, get_graph, set_graph
from architecto.core.config.agent import AgentSettings
from architecto.core.config.database import DatabaseSettings


def test_defaut_est_le_graphe_memoire():
    set_graph(None)
    assert get_graph() is build_graph()  # lru_cache -> même instance


def test_set_graph_prime_puis_reset(monkeypatch):
    sentinel = object()
    set_graph(sentinel)
    try:
        assert get_graph() is sentinel
    finally:
        set_graph(None)
    assert get_graph() is build_graph()


def test_build_graph_with_compile_un_graphe_executable():
    from langgraph.checkpoint.memory import MemorySaver

    compiled = graph.build_graph_with(MemorySaver())
    # un graphe compilé expose l'API d'exécution/streaming
    assert hasattr(compiled, "ainvoke")
    assert hasattr(compiled, "astream_events")


def test_checkpointer_par_defaut_est_memoire():
    assert AgentSettings().checkpointer == "memory"


def test_psycopg_dsn_sans_driver_sqlalchemy():
    db = DatabaseSettings(host="db", port=5432, user="u", name="n")
    dsn = db.psycopg_dsn
    assert dsn.startswith("postgresql://u:")
    assert "@db:5432/n" in dsn
    assert "+psycopg" not in dsn
