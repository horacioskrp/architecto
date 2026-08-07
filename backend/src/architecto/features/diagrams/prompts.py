# Types de diagrammes exposés -> directive Mermaid correspondante.
DIAGRAM_TYPES = {
    "class": "classDiagram",
    "sequence": "sequenceDiagram",
    "flowchart": "flowchart TD",
    "component": "flowchart TD",
    "er": "erDiagram",
    "state": "stateDiagram-v2",
}

DIAGRAM_SYSTEM_PROMPT = """Tu es un générateur de diagrammes Mermaid.
Produis UNIQUEMENT du code Mermaid valide de type `{mermaid_type}`, à partir de la
description fournie par l'utilisateur.

Règles :
- Commence directement par la directive Mermaid `{mermaid_type}`.
- Aucun texte explicatif, aucune fence Markdown (pas de ```).
- Nomme clairement les entités et relations ; garde le diagramme lisible.
"""
