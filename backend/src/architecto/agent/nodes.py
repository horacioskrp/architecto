from langchain_core.messages import SystemMessage

from architecto.agent.prompts import SYSTEM_PROMPT
from architecto.agent.state import AgentState
from architecto.agent.tools import TOOLS
from architecto.core.llm import get_llm


def agent_node(state: AgentState) -> dict:
    """Nœud principal : le LLM (avec tools liés) répond ou demande un appel d'outil."""
    llm = get_llm().bind_tools(TOOLS)
    system = SystemMessage(content=SYSTEM_PROMPT.format(context=state.get("context", "")))
    response = llm.invoke([system, *state["messages"]])
    return {"messages": [response]}
