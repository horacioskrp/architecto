from __future__ import annotations

from typing import TYPE_CHECKING

from architecto.core.llm.base import ChatAdapter, EmbeddingAdapter
from architecto.core.llm.registry import register_chat, register_embedding

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel

    from architecto.core.config.embeddings import EmbeddingSettings
    from architecto.core.config.llm import ChatModelSettings


class GoogleChat(ChatAdapter):
    provider = "google"

    def build(self, config: ChatModelSettings) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=config.model,
            google_api_key=config.api_key.get_secret_value() or None,
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
            timeout=config.timeout,
        )


class GoogleEmbedding(EmbeddingAdapter):
    provider = "google"

    def build(self, config: EmbeddingSettings) -> Embeddings:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=config.model,
            google_api_key=config.api_key.get_secret_value() or None,
        )


register_chat(GoogleChat())
register_embedding(GoogleEmbedding())
