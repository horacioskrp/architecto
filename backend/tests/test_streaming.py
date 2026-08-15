import pytest
from langchain_core.messages import AIMessage

from architecto.agent import graph
from architecto.agent.graph import _text, stream_agent


class _Chunk:
    def __init__(self, content) -> None:
        self.content = content


class _Snapshot:
    def __init__(self, messages) -> None:
        self.values = {"messages": messages}


class _FakeGraph:
    """Graphe factice : rejoue une liste d'évènements astream_events."""

    def __init__(self, events, final=None) -> None:
        self._events = events
        self._final = final or []

    async def astream_events(self, _inputs, *, config, version):  # noqa: ARG002
        for event in self._events:
            yield event

    async def aget_state(self, _config):
        return _Snapshot(self._final)


def _delta_event(text, node="agent"):
    return {
        "event": "on_chat_model_stream",
        "metadata": {"langgraph_node": node},
        "data": {"chunk": _Chunk(text)},
    }


async def _collect(agen):
    return [chunk async for chunk in agen]


def test_text_aplati_str_et_blocs():
    assert _text("bonjour") == "bonjour"
    assert _text([{"text": "a"}, {"text": "b"}]) == "ab"
    assert _text(["x", "y"]) == "xy"


@pytest.mark.asyncio
async def test_stream_relaie_les_tokens_du_noeud_agent(monkeypatch):
    events = [
        _delta_event("{", node="triage"),  # sortie structurée du triage -> ignorée
        _delta_event("Archi"),
        _delta_event("tecto"),
    ]
    monkeypatch.setattr(graph, "build_graph", lambda: _FakeGraph(events))

    out = await _collect(stream_agent("salut", thread_id="t", project="p"))
    assert out == [
        {"type": "delta", "text": "Archi"},
        {"type": "delta", "text": "tecto"},
    ]


@pytest.mark.asyncio
async def test_stream_relaie_les_evenements_outils(monkeypatch):
    events = [
        {"event": "on_tool_start", "name": "generate_diagram", "metadata": {}, "data": {}},
        {"event": "on_tool_end", "name": "generate_diagram", "metadata": {}, "data": {}},
        _delta_event("Voici"),
    ]
    monkeypatch.setattr(graph, "build_graph", lambda: _FakeGraph(events))

    out = await _collect(stream_agent("diagramme"))
    assert out == [
        {"type": "tool", "name": "generate_diagram", "phase": "start"},
        {"type": "tool", "name": "generate_diagram", "phase": "end"},
        {"type": "delta", "text": "Voici"},
    ]


@pytest.mark.asyncio
async def test_stream_fallback_emet_le_message_final(monkeypatch):
    # Aucun token diffusé (chemin clarify) -> on émet le contenu final en une fois.
    final = [AIMessage(content="Il me manque des précisions.")]
    monkeypatch.setattr(graph, "build_graph", lambda: _FakeGraph([], final=final))

    out = await _collect(stream_agent("salut"))
    assert out == [{"type": "delta", "text": "Il me manque des précisions."}]


@pytest.mark.asyncio
async def test_stream_fallback_sans_message_ne_produit_rien(monkeypatch):
    monkeypatch.setattr(graph, "build_graph", lambda: _FakeGraph([], final=[]))

    out = await _collect(stream_agent("salut"))
    assert out == []
