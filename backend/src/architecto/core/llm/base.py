from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel

    from architecto.core.config.embeddings import EmbeddingSettings
    from architecto.core.config.llm import ChatModelSettings


class ChatAdapter(ABC):
    """Port : construit un modèle de chat LangChain pour un provider donné.

    Chaque implémentation importe son intégration LangChain *dans* `build()`
    (import paresseux) → on n'installe que le provider réellement utilisé.
    """

    provider: str

    @abstractmethod
    def build(self, config: ChatModelSettings) -> BaseChatModel: ...


class EmbeddingAdapter(ABC):
    """Port : construit un modèle d'embeddings LangChain pour un provider donné."""

    provider: str

    @abstractmethod
    def build(self, config: EmbeddingSettings) -> Embeddings: ...
