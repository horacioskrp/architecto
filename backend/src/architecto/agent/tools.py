"""Registre des outils exposés à l'agent, agrégés depuis les features."""

from architecto.features.adr.tools import generate_adr
from architecto.features.diagrams.tools import generate_diagram
from architecto.features.knowledge.tools import search_knowledge_base

TOOLS = [search_knowledge_base, generate_diagram, generate_adr]

__all__ = ["TOOLS", "generate_adr", "generate_diagram", "search_knowledge_base"]
