from __future__ import annotations

from collections.abc import AsyncIterator

from architecto.agent.graph import run_agent, stream_agent
from architecto.features.chat.ports import ChatAgent


class GraphChatAgent(ChatAgent):
    """Implémentation du port `ChatAgent` par l'agent LangGraph.

    Vit dans la couche `agent` (autorisée à importer `features`), et est câblée
    à la feature `chat` par la racine de composition (`main.py`). Ainsi la
    feature ne remonte jamais vers la couche `agent`.
    """

    async def run(self, message: str, thread_id: str, project: str) -> str:
        return await run_agent(message, thread_id, project)

    def stream(self, message: str, thread_id: str, project: str) -> AsyncIterator[dict]:
        return stream_agent(message, thread_id, project)
