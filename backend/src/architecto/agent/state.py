from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """État partagé entre les nœuds du graphe LangGraph.

    `messages` est réduit par `add_messages` : chaque nœud renvoie les nouveaux
    messages, LangGraph les concatène à l'historique. Les autres champs sont
    optionnels (renseignés par le nœud de triage).
    """

    messages: Annotated[list, add_messages]
    context: str  # extraits RAG injectés avant l'appel LLM
    needs_clarification: bool  # posé par le triage : faut-il clarifier avant de répondre ?
    questions: list[str]  # questions de clarification à poser
