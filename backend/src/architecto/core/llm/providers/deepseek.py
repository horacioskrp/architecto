from __future__ import annotations

from typing import TYPE_CHECKING

from architecto.core.llm.base import ChatAdapter
from architecto.core.llm.registry import register_chat

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from architecto.core.config.llm import ChatModelSettings


class DeepSeekChat(ChatAdapter):
    provider = "deepseek"

    def build(self, config: ChatModelSettings) -> BaseChatModel:
        from langchain_deepseek import ChatDeepSeek

        return ChatDeepSeek(
            model=config.model,
            api_key=config.api_key.get_secret_value() or None,
            api_base=config.base_url or None,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
        )


# DeepSeek n'expose pas d'API d'embeddings : pas d'EmbeddingAdapter.
register_chat(DeepSeekChat())
