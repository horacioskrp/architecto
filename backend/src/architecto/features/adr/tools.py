from langchain_core.tools import tool

from architecto.features.adr.template import render_adr


@tool
def generate_adr(
    title: str,
    context: str,
    decision: str,
    consequences: str,
    alternatives: str = "",
    status: str = "Proposed",
) -> str:
    """Génère un ADR (Architecture Decision Record) structuré en Markdown.

    L'agent fournit le contenu ; l'outil garantit la structure :
    Contexte · Décision · Conséquences · Alternatives considérées.
    `status` : Proposed | Accepted | Deprecated | Superseded.
    """
    return render_adr(
        title=title,
        context=context,
        decision=decision,
        consequences=consequences,
        alternatives=alternatives,
        status=status,
    )
