"""Registre des outils exposés à l'agent, agrégés depuis les features."""

from architecto.features.adr.tools import generate_adr
from architecto.features.analysis.tools import analyze_dependencies
from architecto.features.architecture.tools import generate_architecture
from architecto.features.database.tools import design_database
from architecto.features.diagrams.tools import generate_diagram
from architecto.features.knowledge.tools import search_knowledge_base
from architecto.features.memory.tools import recall_decisions, save_decision
from architecto.features.security.tools import security_checklist

TOOLS = [
    search_knowledge_base,
    generate_diagram,
    generate_adr,
    generate_architecture,
    design_database,
    security_checklist,
    analyze_dependencies,
    save_decision,
    recall_decisions,
]

__all__ = [
    "TOOLS",
    "analyze_dependencies",
    "design_database",
    "generate_adr",
    "generate_architecture",
    "generate_diagram",
    "recall_decisions",
    "save_decision",
    "search_knowledge_base",
    "security_checklist",
]
