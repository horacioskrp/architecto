"""Couche LLM agnostique du provider (pattern Adapter + Registry).

Sélection du provider via la config :
- chat       -> `settings.llm.provider`        (anthropic | openai | google | deepseek)
- embeddings -> `settings.embeddings.provider` (openai | google)

API publique : `get_chat_model()` et `get_embeddings()`.
"""

# Importe les adaptateurs pour peupler les registres.
from architecto.core.llm import providers  # noqa: F401
from architecto.core.llm.base import ChatAdapter, EmbeddingAdapter
from architecto.core.llm.registry import (
    get_chat_model,
    get_embeddings,
    register_chat,
    register_embedding,
)

__all__ = [
    "ChatAdapter",
    "EmbeddingAdapter",
    "get_chat_model",
    "get_embeddings",
    "register_chat",
    "register_embedding",
]
