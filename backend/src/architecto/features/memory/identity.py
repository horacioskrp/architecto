from __future__ import annotations

DEFAULT_PROJECT = "default"


def _clean(value: str | None) -> str:
    return value.strip() if value else ""


def resolve_project(slug: str | None = None, thread_id: str | None = None) -> str:
    """Identité du projet : slug si fourni, sinon thread_id, sinon `default`."""
    return _clean(slug) or _clean(thread_id) or DEFAULT_PROJECT
