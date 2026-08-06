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


async def run_agent(message: str, thread_id: str = "default") -> str:
    """Exécute un tour de conversation et renvoie la réponse texte de l'agent."""
    app = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = await app.ainvoke(
        {"messages": [HumanMessage(content=message)], "context": ""},
        config=config,
    )
    return result["messages"][-1].content
