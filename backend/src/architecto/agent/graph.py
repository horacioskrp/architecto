from collections.abc import AsyncIterator
from functools import lru_cache

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from architecto.agent.nodes import agent_node, clarify_node, route_after_triage, triage_node
from architecto.agent.state import AgentState
from architecto.agent.tools import TOOLS


@lru_cache
def build_graph():
    """Construit le graphe agentique.

    Flux : triage décide s'il faut clarifier.
    - clarification requise -> `clarify` (pose des questions) -> END
    - sinon -> `agent` <-> `tools` (boucle ReAct) -> END

    Note : checkpointer en mémoire pour le squelette. En production, remplacer par
    `AsyncPostgresSaver` (langgraph-checkpoint-postgres) pour persister les threads.
    """
    from langgraph.checkpoint.memory import MemorySaver

    graph = StateGraph(AgentState)
    graph.add_node("triage", triage_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "triage")
    graph.add_conditional_edges(
        "triage", route_after_triage, {"clarify": "clarify", "agent": "agent"}
    )
    graph.add_edge("clarify", END)
    # tools_condition aiguille agent -> "tools" ou agent -> END (fin du tour)
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=MemorySaver())


def _configize(thread_id: str, project: str) -> dict:
    return {"configurable": {"thread_id": thread_id, "project": project}}


def _text(content: object) -> str:
    """Aplati le contenu d'un chunk (str ou blocs) en texte."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text", "")))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content)


async def run_agent(message: str, thread_id: str = "default", project: str = "") -> str:
    """Exécute un tour de conversation et renvoie la réponse texte de l'agent.

    `project` (optionnel) scope la mémoire long terme (save/recall_decisions).
    """
    app = build_graph()
    result = await app.ainvoke(
        {"messages": [HumanMessage(content=message)], "context": ""},
        config=_configize(thread_id, project),
    )
    return result["messages"][-1].content


async def stream_agent(
    message: str, thread_id: str = "default", project: str = ""
) -> AsyncIterator[str]:
    """Diffuse la réponse de l'agent en flux de deltas texte.

    On ne relaie que les tokens du nœud `agent` (le triage utilise une sortie
    structurée, à ignorer). Si aucun token n'a été diffusé — chemin `clarify`
    ou tour purement outillé — on émet le contenu final en une fois.
    """
    app = build_graph()
    config = _configize(thread_id, project)
    inputs = {"messages": [HumanMessage(content=message)], "context": ""}

    streamed = False
    async for event in app.astream_events(inputs, config=config, version="v2"):
        if event.get("event") != "on_chat_model_stream":
            continue
        if event.get("metadata", {}).get("langgraph_node") != "agent":
            continue
        delta = _text(event["data"]["chunk"].content)
        if delta:
            streamed = True
            yield delta

    if not streamed:
        snapshot = await app.aget_state(config)
        messages = snapshot.values.get("messages", [])
        if messages:
            content = _text(messages[-1].content)
            if content:
                yield content
