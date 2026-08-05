from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from architecto.core.config import settings
from architecto.core.llm.base import ChatAdapter, EmbeddingAdapter

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel

_CHAT: dict[str, ChatAdapter] = {}
_EMBED: dict[str, EmbeddingAdapter] = {}

#: Provider -> package d'intégration à installer (pour les messages d'erreur).
_EXTRAS = {
    "openai": "langchain-openai",
    "anthropic": "langchain-anthropic",
    "google": "langchain-google-genai",
    "deepseek": "langchain-deepseek",
}


def register_chat(adapter: ChatAdapter) -> None:
    _CHAT[adapter.provider] = adapter


def register_embedding(adapter: EmbeddingAdapter) -> None:
    _EMBED[adapter.provider] = adapter


def _resolve(registry: dict, provider: str, kind: str):
    adapter = registry.get(provider)
    if adapter is None:
        raise ValueError(
            f"Provider {kind} inconnu : {provider!r}. Disponibles : {sorted(registry)}"
        )
    return adapter


def _build(adapter, config, provider: str):
    try:
        return adapter.build(config)
    except ImportError as exc:  # intégration LangChain non installée
        pkg = _EXTRAS.get(provider, "")
        raise RuntimeError(
            f"Intégration manquante pour le provider {provider!r}. "
            f"Installe-la : uv add {pkg}"
        ) from exc


@lru_cache(maxsize=1)
def get_chat_model() -> BaseChatModel:
    """Modèle de chat du provider configuré (`settings.llm.provider`)."""
    adapter = _resolve(_CHAT, settings.llm.provider, "chat")
    return _build(adapter, settings.llm, settings.llm.provider)


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    """Modèle d'embeddings du provider configuré (`settings.embeddings.provider`)."""
    adapter = _resolve(_EMBED, settings.embeddings.provider, "embeddings")
    return _build(adapter, settings.embeddings, settings.embeddings.provider)
