from langchain_core.messages import AIMessage

from architecto.agent import nodes
from architecto.agent.nodes import Triage, clarify_node, route_after_triage, triage_node


def test_route_vers_clarify_quand_info_manque():
    assert route_after_triage({"needs_clarification": True}) == "clarify"


def test_route_vers_agent_quand_info_suffisante():
    assert route_after_triage({"needs_clarification": False}) == "agent"


def test_route_defaut_vers_agent():
    # champ absent -> on ne bloque pas l'utilisateur
    assert route_after_triage({}) == "agent"


def test_clarify_node_formate_les_questions():
    out = clarify_node({"questions": ["Quel langage ?", "Quelle charge attendue ?"]})
    message = out["messages"][0]
    assert isinstance(message, AIMessage)
    assert "- Quel langage ?" in message.content
    assert "- Quelle charge attendue ?" in message.content


def test_clarify_node_sans_questions():
    out = clarify_node({})
    assert isinstance(out["messages"][0], AIMessage)
    assert out["messages"][0].content  # message non vide


def test_triage_node_mappe_la_decision(monkeypatch):
    """triage_node traduit la décision structurée du LLM en état, sans vrai LLM."""

    class _FakeStructured:
        def invoke(self, _messages):
            return Triage(needs_clarification=True, questions=["Préciser le domaine ?"])

    class _FakeLLM:
        def with_structured_output(self, _schema):
            return _FakeStructured()

    monkeypatch.setattr(nodes, "get_chat_model", lambda: _FakeLLM())

    out = triage_node({"messages": []})
    assert out["needs_clarification"] is True
    assert out["questions"] == ["Préciser le domaine ?"]
