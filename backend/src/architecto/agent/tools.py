"""Registre des outils exposés à l'agent, agrégés depuis les features."""

from architecto.features.knowledge.tools import search_knowledge_base

TOOLS = [search_knowledge_base]

__all__ = ["TOOLS", "search_knowledge_base"]
