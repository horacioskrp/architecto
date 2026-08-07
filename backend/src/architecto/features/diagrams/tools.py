from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from architecto.core.llm import get_chat_model
from architecto.features.diagrams.prompts import DIAGRAM_SYSTEM_PROMPT, DIAGRAM_TYPES


def strip_code_fences(text: str) -> str:
    """Retire d'éventuelles fences ``` / ```mermaid autour du code renvoyé par le LLM."""
    lines = text.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def wrap_mermaid(code: str) -> str:
    """Encadre le code dans un bloc ```mermaid prêt à afficher."""
    return f"```mermaid\n{code}\n```"


def resolve_type(diagram_type: str) -> str:
    """Directive Mermaid pour un type demandé (repli sur `classDiagram`)."""
    return DIAGRAM_TYPES.get(diagram_type.lower(), DIAGRAM_TYPES["class"])


@tool
def generate_diagram(description: str, diagram_type: str = "class") -> str:
    """Génère un diagramme Mermaid à partir d'une description.

    `diagram_type` : class | sequence | component | flowchart | er | state.
    À utiliser pour illustrer une architecture, un flux ou un modèle de données.
    Renvoie un bloc ```mermaid``` prêt à afficher.
    """
    mermaid_type = resolve_type(diagram_type)
    system = DIAGRAM_SYSTEM_PROMPT.format(mermaid_type=mermaid_type)
    response = get_chat_model().invoke(
        [SystemMessage(content=system), HumanMessage(content=description)]
    )
    code = strip_code_fences(str(response.content))
    return wrap_mermaid(code)
