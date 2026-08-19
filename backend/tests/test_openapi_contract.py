"""Garde-fou du contrat : `backend/openapi.json` doit rester à jour.

Ce fichier committé est la source de vérité dont dérivent le frontend (types
TypeScript via `openapi-typescript`) et le SDK Python (test de conformité).
S'il est périmé, la dérive se propage silencieusement — ce test l'empêche.
"""

import json
from pathlib import Path

from architecto.main import app

OPENAPI = Path(__file__).resolve().parents[1] / "openapi.json"


def _serialize(schema: dict) -> str:
    # Doit être identique à scripts/dump_openapi.py.
    return json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def test_openapi_json_committe_est_a_jour():
    expected = _serialize(app.openapi())
    actual = OPENAPI.read_text(encoding="utf-8")
    assert actual == expected, (
        "backend/openapi.json est périmé par rapport aux schémas de l'app. "
        "Régénère-le : `uv run python scripts/dump_openapi.py` "
        "(le frontend et le SDK Python en dérivent)."
    )
