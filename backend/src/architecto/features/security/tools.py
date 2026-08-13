from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from architecto.core.llm import get_chat_model
from architecto.features.security.prompts import build_system_prompt


@tool
def security_checklist(description: str) -> str:
    """Génère une checklist de sécurité **ancrée OWASP Top 10** pour le système décrit.

    Sortie = points à vérifier par catégorie OWASP (cases à cocher). C'est une checklist
    de vérification, **jamais un verdict** sur le niveau de sécurité.
    """
    response = get_chat_model().invoke(
        [SystemMessage(content=build_system_prompt()), HumanMessage(content=description)]
    )
    return str(response.content).strip()
