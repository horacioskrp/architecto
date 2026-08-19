from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol


class ChatAgent(Protocol):
    """Port consommé par la feature `chat`.

    La feature dépend de cette abstraction, pas de la couche `agent` : c'est une
    inversion de dépendance qui respecte la direction des couches
    (`features -> core` uniquement). L'implémentation concrète — l'agent
    LangGraph — est fournie par la couche `agent` et injectée à la racine de
    composition (`main.py`), jamais importée ici.
    """

    async def run(self, message: str, thread_id: str, project: str) -> str: ...

    def stream(self, message: str, thread_id: str, project: str) -> AsyncIterator[dict]: ...


def get_chat_agent() -> ChatAgent:
    """Dépendance FastAPI, surchargée à la racine de composition (`main.py`).

    Sans surcharge, aucun agent n'est câblé : on lève explicitement plutôt que
    d'échouer silencieusement.
    """
    raise RuntimeError("ChatAgent non configuré : dependency_overrides manquant.")
