"""Exporte le schéma OpenAPI de l'API dans `backend/openapi.json`.

Source de vérité du contrat front/back : le frontend génère ses types TypeScript
à partir de ce fichier (voir `frontend` → script `gen:api`). Régénérer après
toute modification des schémas/endpoints :

    uv run python scripts/dump_openapi.py

N'a besoin ni de la base ni du LLM (l'app s'importe sans effet de bord).
"""

import json
from pathlib import Path

from architecto.main import app

OUTPUT = Path(__file__).resolve().parents[1] / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths = len(schema.get("paths", {}))
    schemas = len(schema.get("components", {}).get("schemas", {}))
    print(f"OpenAPI écrit → {OUTPUT}  ({paths} chemins, {schemas} schémas)")


if __name__ == "__main__":
    main()
