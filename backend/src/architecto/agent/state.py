from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """État partagé entre les nœuds du graphe LangGraph.

    `messages` est réduit par `add_messages` : chaque nœud renvoie les nouveaux
    messages, LangGraph les concatène à l'historique.
    """

    messages: Annotated[list, add_messages]
    context: str  # extraits RAG injectés avant l'appel LLM
