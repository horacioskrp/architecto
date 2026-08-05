from functools import lru_cache

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from architecto.agent.nodes import agent_node
from architecto.agent.state import AgentState
from architecto.agent.tools import TOOLS


@lru_cache
def build_graph():
    """Construit le graphe agentique : agent <-> tools, boucle ReAct.

    Note : checkpointer en mémoire pour le squelette. En production, remplacer par
    `AsyncPostgresSaver` (langgraph-checkpoint-postgres) pour persister les threads.
    """
    from langgraph.checkpoint.memory import MemorySaver

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    graph.add_edge("agent", END)

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
