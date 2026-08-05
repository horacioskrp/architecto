"""Import des adaptateurs pour peupler les registres au chargement du package.

L'import d'un module d'adaptateur est léger : les intégrations LangChain lourdes
ne sont importées que dans `build()` (import paresseux).
"""

from architecto.core.llm.providers import anthropic, deepseek, google, openai

__all__ = ["anthropic", "deepseek", "google", "openai"]
