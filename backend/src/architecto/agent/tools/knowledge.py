from langchain_core.tools import tool

from architecto.db.vectorstore import get_vectorstore


@tool
def search_knowledge_base(query: str, k: int = 4) -> str:
    """Recherche dans la base de connaissances d'architecture (patterns, ADR, best practices).

    À utiliser dès qu'une question porte sur des choix techniques documentés.
    """
    store = get_vectorstore()
    docs = store.similarity_search(query, k=k)
    if not docs:
        return "Aucun document pertinent trouvé."
    return "\n\n---\n\n".join(d.page_content for d in docs)
