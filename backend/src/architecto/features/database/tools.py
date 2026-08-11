from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from architecto.core.llm import get_chat_model
from architecto.features.database.prompts import DATABASE_SYSTEM_PROMPT
from architecto.features.database.sql import extract_sql, validate_sql


@tool
def design_database(description: str) -> str:
    """Conçoit un schéma relationnel PostgreSQL (entités, clés, FK, index).

    Génère le DDL puis **valide sa syntaxe** (sqlglot) et signale le résultat.
    À utiliser dès qu'il faut modéliser des données.
    """
    response = get_chat_model().invoke(
        [SystemMessage(content=DATABASE_SYSTEM_PROMPT), HumanMessage(content=description)]
    )
    text = str(response.content).strip()
    ok, error = validate_sql(extract_sql(text))
    status = (
        "✅ DDL PostgreSQL syntaxiquement valide."
        if ok
        else f"⚠️ Erreur de syntaxe SQL : {error}"
    )
    return f"{text}\n\n---\n{status}"
