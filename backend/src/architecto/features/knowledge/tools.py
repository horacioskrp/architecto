from collections.abc import Sequence
from typing import Any

from langchain_core.tools import tool

from architecto.features.knowledge.vectorstore import get_vectorstore


def format_results(docs: Sequence[Any]) -> str:
    """Formate les extraits en les **numérotant** et en exposant leur source.

    Chaque bloc `[n] <titre> — <source>` permet à l'agent de citer précisément.
    """
    blocks = []
    for index, doc in enumerate(docs, start=1):
        metadata = getattr(doc, "metadata", None) or {}
        title = metadata.get("title") or "(sans titre)"
        source = metadata.get("source") or "(source inconnue)"
        blocks.append(f"[{index}] {title} — {source}\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)


@tool
def search_knowledge_base(query: str, k: int = 4) -> str:
    """Recherche dans la base de connaissances d'architecture (patterns, ADR, best practices).

    À utiliser dès qu'une question porte sur des choix techniques documentés.
    Renvoie des extraits numérotés avec leur source, à citer dans la réponse.
    """
    store = get_vectorstore()
    docs = store.similarity_search(query, k=k)
    if not docs:
        return "Aucun document pertinent trouvé."
    return format_results(docs)
