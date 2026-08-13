# LLM providers (adapter architecture)

> 🇫🇷 [Version française](../fr/llm-providers.md)

The LLM layer is **provider-agnostic**: Claude, OpenAI, Gemini or DeepSeek are
interchangeable **by configuration, without touching the code**.

## Why an adapter

- **Stable port**: the rest of the code depends on an abstraction (`ChatModel` /
  `Embeddings`), not a specific SDK.
- **Lazy imports**: each adapter imports its LangChain integration only inside
  `build()` → you install only the provider you use.
- **Chat ≠ embeddings**: Anthropic provides no embeddings, so the two providers
  are decoupled.

## Layout

```
core/llm/
├── base.py            # ports: ChatAdapter / EmbeddingAdapter (ABC)
├── registry.py        # get_chat_model() / get_embeddings() + registries
└── providers/
    ├── anthropic.py   # Claude          (chat)
    ├── openai.py      # GPT + embeddings
    ├── google.py      # Gemini + embeddings
    └── deepseek.py    # DeepSeek         (chat, OpenAI-compatible)
```

## Selection by configuration

```bash
# Chat
LLM_PROVIDER=anthropic      # anthropic | openai | google | deepseek
LLM_MODEL=claude-sonnet-5
LLM_API_KEY=sk-ant-...

# Embeddings (independent)
EMBEDDING_PROVIDER=openai   # openai | google
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-...
```

### Examples

| Goal | Config |
|------|--------|
| Claude + OpenAI embeddings (default) | `LLM_PROVIDER=anthropic`, `EMBEDDING_PROVIDER=openai` |
| GPT-4o mini everywhere | `LLM_PROVIDER=openai LLM_MODEL=gpt-4o-mini` |
| Gemini + Google embeddings | `LLM_PROVIDER=google LLM_MODEL=gemini-2.5-flash`, `EMBEDDING_PROVIDER=google` |
| DeepSeek (OpenAI-compatible) | `LLM_PROVIDER=deepseek LLM_MODEL=deepseek-chat LLM_BASE_URL=https://api.deepseek.com` |
| DeepSeek + **local** embeddings | `LLM_PROVIDER=deepseek …`, `EMBEDDING_PROVIDER=local` |

### Embeddings

`EMBEDDING_PROVIDER` ∈ `openai` \| `google` \| **`local`**. The **`local`** provider
(fastembed) runs **without a key** (a small ONNX model downloaded on first use) — ideal
for a DeepSeek/Claude chat with no embeddings API, or for offline RAG.

## Installing providers

The base install ships **Anthropic** (default chat) and **OpenAI** (embeddings).
For the others, the integration is an optional extra:

```bash
uv add langchain-google-genai     # Gemini
uv add langchain-deepseek         # DeepSeek (chat)
uv add fastembed                  # local embeddings (EMBEDDING_PROVIDER=local)
```

If the package is missing, the call fails with an explicit message:

```
Intégration manquante pour le provider 'deepseek'. Installe-la : uv add langchain-deepseek
```

## Usage in code

```python
from architecto.core.llm import get_chat_model, get_embeddings

llm = get_chat_model()          # provider = settings.llm.provider
embeddings = get_embeddings()   # provider = settings.embeddings.provider
```

Both functions are memoized (one instance per process).

## Adding a provider

1. Create `core/llm/providers/<name>.py` with a class inheriting from `ChatAdapter`
   (and/or `EmbeddingAdapter`) that imports its integration **inside `build()`**.
2. Register it: `register_chat(MyAdapter())`.
3. Import it in `core/llm/providers/__init__.py`.
4. Add the provider to the `ChatProvider` type (config) and to `_EXTRAS` (registry).
5. Document it here (EN) and in the equivalent FR page.

Minimal example:

```python
from __future__ import annotations
from typing import TYPE_CHECKING
from architecto.core.llm.base import ChatAdapter
from architecto.core.llm.registry import register_chat

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from architecto.core.config.llm import ChatModelSettings


class MyProviderChat(ChatAdapter):
    provider = "my_provider"

    def build(self, config: ChatModelSettings) -> BaseChatModel:
        from langchain_xxx import ChatXxx      # lazy import
        return ChatXxx(model=config.model, api_key=config.api_key.get_secret_value() or None)


register_chat(MyProviderChat())
```
