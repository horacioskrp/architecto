from __future__ import annotations

from typing import TYPE_CHECKING

from architecto.core.llm.base import ChatAdapter, EmbeddingAdapter
from architecto.core.llm.registry import register_chat, register_embedding

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel

    from architecto.core.config.embeddings import EmbeddingSettings
    from architecto.core.config.llm import ChatModelSettings


class OpenAIChat(ChatAdapter):
    provider = "openai"

    def build(self, config: ChatModelSettings) -> BaseChatModel:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key.get_secret_value() or None,
            base_url=config.base_url,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
        )


class OpenAIEmbedding(EmbeddingAdapter):
    provider = "openai"

    def build(self, config: EmbeddingSettings) -> Embeddings:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=config.model,
            api_key=config.api_key.get_secret_value() or None,
            base_url=config.base_url,
        )


register_chat(OpenAIChat())
register_embedding(OpenAIEmbedding())
