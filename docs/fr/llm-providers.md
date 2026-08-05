# Providers LLM (architecture adaptateur)

> 🇬🇧 [English version](../en/llm-providers.md)

La couche LLM est **agnostique du provider** : Claude, OpenAI, Gemini ou DeepSeek
sont interchangeables **par configuration, sans toucher au code**.

## Pourquoi un adaptateur

- **Port stable** : le reste du code dépend d'une abstraction (`ChatModel` /
  `Embeddings`), pas d'un SDK précis.
- **Imports paresseux** : chaque adaptateur importe son intégration LangChain
  seulement dans `build()` → on n'installe que le provider utilisé.
- **Chat ≠ embeddings** : Anthropic ne fournit pas d'embeddings, les deux
  providers sont donc découplés.

## Organisation

```
core/llm/
├── base.py            # ports : ChatAdapter / EmbeddingAdapter (ABC)
├── registry.py        # get_chat_model() / get_embeddings() + registres
└── providers/
    ├── anthropic.py   # Claude          (chat)
    ├── openai.py      # GPT + embeddings
    ├── google.py      # Gemini + embeddings
    └── deepseek.py    # DeepSeek         (chat, OpenAI-compatible)
```

## Sélection par configuration

```bash
# Chat
LLM_PROVIDER=anthropic      # anthropic | openai | google | deepseek
LLM_MODEL=claude-sonnet-5
LLM_API_KEY=sk-ant-...

# Embeddings (indépendant)
EMBEDDING_PROVIDER=openai   # openai | google
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-...
```

### Exemples

| Objectif | Config |
|----------|--------|
| Claude + embeddings OpenAI (défaut) | `LLM_PROVIDER=anthropic`, `EMBEDDING_PROVIDER=openai` |
| GPT-4o mini partout | `LLM_PROVIDER=openai LLM_MODEL=gpt-4o-mini` |
| Gemini + embeddings Google | `LLM_PROVIDER=google LLM_MODEL=gemini-2.5-flash`, `EMBEDDING_PROVIDER=google` |
| DeepSeek (OpenAI-compatible) | `LLM_PROVIDER=deepseek LLM_MODEL=deepseek-chat LLM_BASE_URL=https://api.deepseek.com` |

## Installation des providers

La base installe **Anthropic** (chat par défaut) et **OpenAI** (embeddings). Pour
les autres, l'intégration est un extra optionnel :

```bash
uv add langchain-google-genai     # Gemini
uv add langchain-deepseek         # DeepSeek
```

Si le package n'est pas installé, l'appel échoue avec un message explicite :

```
Intégration manquante pour le provider 'deepseek'. Installe-la : uv add langchain-deepseek
```

## Utilisation dans le code

```python
from architecto.core.llm import get_chat_model, get_embeddings

llm = get_chat_model()          # provider = settings.llm.provider
embeddings = get_embeddings()   # provider = settings.embeddings.provider
```

Les deux fonctions sont mémoïsées (une instance par process).

## Ajouter un provider

1. Créer `core/llm/providers/<nom>.py` avec une classe qui hérite de `ChatAdapter`
   (et/ou `EmbeddingAdapter`) et importe son intégration **dans `build()`**.
2. L'enregistrer : `register_chat(MonAdapter())`.
3. L'importer dans `core/llm/providers/__init__.py`.
4. Ajouter le provider au type `ChatProvider` (config) et à `_EXTRAS` (registry).
5. Documenter ici (FR) et dans la page EN équivalente.

Exemple minimal :

```python
from __future__ import annotations
from typing import TYPE_CHECKING
from architecto.core.llm.base import ChatAdapter
from architecto.core.llm.registry import register_chat

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from architecto.core.config.llm import ChatModelSettings


class MonProviderChat(ChatAdapter):
    provider = "mon_provider"

    def build(self, config: ChatModelSettings) -> BaseChatModel:
        from langchain_xxx import ChatXxx      # import paresseux
        return ChatXxx(model=config.model, api_key=config.api_key.get_secret_value() or None)


register_chat(MonProviderChat())
```
