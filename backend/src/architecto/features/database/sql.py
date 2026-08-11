from __future__ import annotations

import re

_SQL_FENCE = re.compile(r"```sql\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_sql(text: str) -> str:
    """Extrait le contenu du premier bloc ```sql ; repli sur le texte nettoyé."""
    match = _SQL_FENCE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip().strip("`").strip()


def validate_sql(sql: str) -> tuple[bool, str]:
    """Valide la **syntaxe** d'un DDL PostgreSQL via sqlglot (aucune base requise).

    Renvoie `(True, "")` si le SQL parse, sinon `(False, message)`.
    """
    if not sql.strip():
        return False, "SQL vide"

    import sqlglot
    from sqlglot.errors import ParseError

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except ParseError as exc:
        return False, str(exc).splitlines()[0]

    if not any(statement is not None for statement in statements):
        return False, "aucune instruction SQL détectée"
    return True, ""
