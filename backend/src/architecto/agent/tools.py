"""Registre des outils exposés à l'agent, agrégés depuis les features."""

from architecto.features.diagrams.tools import generate_diagram
from architecto.features.knowledge.tools import search_knowledge_base

TOOLS = [search_knowledge_base, generate_diagram]

__all__ = ["TOOLS", "generate_diagram", "search_knowledge_base"]
