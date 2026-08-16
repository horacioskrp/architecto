from __future__ import annotations

from datetime import date as date_cls

ADR_STATUSES = ("Proposed", "Accepted", "Deprecated", "Superseded")


def normalize_status(status: str) -> str:
    """Repli sur `Proposed` si le statut n'est pas reconnu."""
    return status if status in ADR_STATUSES else "Proposed"


def render_adr(
    *,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    alternatives: str = "",
    status: str = "Proposed",
    adr_date: str | None = None,
) -> str:
    """Rend un ADR Markdown structuré (fonction pure, structure garantie)."""
    # date locale volontaire : un ADR est daté du jour, sans notion de fuseau.
    day = adr_date or date_cls.today().isoformat()  # noqa: DTZ011
    alts = alternatives.strip() or "—"
    return (
        f"# ADR : {title.strip()}\n\n"
        f"- **Statut** : {normalize_status(status)}\n"
        f"- **Date** : {day}\n\n"
        f"## Contexte\n\n{context.strip()}\n\n"
        f"## Décision\n\n{decision.strip()}\n\n"
        f"## Conséquences\n\n{consequences.strip()}\n\n"
        f"## Alternatives considérées\n\n{alts}\n"
    )
