from __future__ import annotations

from typing import TYPE_CHECKING

from architecto.core.llm.base import EmbeddingAdapter
from architecto.core.llm.registry import register_embedding

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

    from architecto.core.config.embeddings import EmbeddingSettings

# Modèle local par défaut (petit, rapide) si aucun modèle fastembed n'est configuré.
DEFAULT_LOCAL_MODEL = "BAAI/bge-small-en-v1.5"


class _FastEmbedEmbeddings:
    """Adaptateur LangChain minimal autour de fastembed (embeddings locaux, sans clé)."""

    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(list(texts))]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.embed([text]))).tolist()


class LocalEmbedding(EmbeddingAdapter):
    provider = "local"

    def build(self, config: EmbeddingSettings) -> Embeddings:
        # Un id fastembed ressemble à "org/nom" ; sinon on prend le défaut local.
        model = config.model if "/" in config.model else DEFAULT_LOCAL_MODEL
        return _FastEmbedEmbeddings(model)  # type: ignore[return-value]


register_embedding(LocalEmbedding())
