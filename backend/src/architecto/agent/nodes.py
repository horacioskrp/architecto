from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from pydantic import BaseModel, Field

from architecto.agent.prompts import SYSTEM_PROMPT, TRIAGE_PROMPT
from architecto.agent.state import AgentState
from architecto.agent.tools import TOOLS
from architecto.core.llm import get_chat_model


class Triage(BaseModel):
    """Décision de triage : faut-il clarifier avant de répondre ?"""

    needs_clarification: bool = Field(
        description="True si des informations essentielles manquent pour proposer une architecture."
    )
    questions: list[str] = Field(
        default_factory=list,
        description="Questions de clarification ciblées (uniquement si needs_clarification).",
    )


def triage_node(state: AgentState) -> dict:
    """Évalue si des informations essentielles manquent (sortie structurée)."""
    llm = get_chat_model().with_structured_output(Triage)
    decision = llm.invoke([SystemMessage(content=TRIAGE_PROMPT), *state["messages"]])
    return {
        "needs_clarification": bool(decision.needs_clarification),
        "questions": list(decision.questions),
    }


def route_after_triage(state: AgentState) -> Literal["clarify", "agent"]:
    """Aiguille : vers la clarification si besoin, sinon vers l'agent."""
    return "clarify" if state.get("needs_clarification") else "agent"


def clarify_node(state: AgentState) -> dict:
    """Émet un message posant les questions de clarification, puis termine le tour."""
    questions = state.get("questions") or []
    intro = "Pour te proposer une architecture pertinente, il me manque quelques précisions :"
    body = "\n".join(f"- {q}" for q in questions)
    content = f"{intro}\n{body}" if body else intro
    return {"messages": [AIMessage(content=content)]}


def agent_node(state: AgentState) -> dict:
    """Nœud principal : le LLM (avec tools liés) répond ou demande un appel d'outil."""
    llm = get_chat_model().bind_tools(TOOLS)
    system = SystemMessage(content=SYSTEM_PROMPT.format(context=state.get("context", "")))
    response = llm.invoke([system, *state["messages"]])
    return {"messages": [response]}
