from __future__ import annotations

from typing import TYPE_CHECKING

from architecto.core.llm.base import ChatAdapter
from architecto.core.llm.registry import register_chat

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from architecto.core.config.llm import ChatModelSettings

#: Anthropic exige max_tokens ; valeur de repli si non configurée.
_DEFAULT_MAX_TOKENS = 4096


class AnthropicChat(ChatAdapter):
    provider = "anthropic"

    def build(self, config: ChatModelSettings) -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=config.model,
            api_key=config.api_key.get_secret_value() or None,
            temperature=config.temperature,
            max_tokens=config.max_tokens or _DEFAULT_MAX_TOKENS,
            timeout=config.timeout,
        )


# Anthropic ne fournit pas d'embeddings : pas d'EmbeddingAdapter.
register_chat(AnthropicChat())
