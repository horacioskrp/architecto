from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from architecto.core.llm import get_chat_model
from architecto.features.architecture.prompts import build_system_prompt


@tool
def generate_architecture(description: str, style: str = "") -> str:
    """Propose une architecture logicielle **orientée compromis** pour un besoin décrit.

    Sortie Markdown : style justifié, découpage en modules (frontières + couplages),
    et section « Compromis » explicite — jamais une simple liste de modules.
    `style` : style suggéré à évaluer (optionnel).
    """
    system = build_system_prompt(style)
    response = get_chat_model().invoke(
        [SystemMessage(content=system), HumanMessage(content=description)]
    )
    return str(response.content).strip()
