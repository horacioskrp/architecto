"""Garde-fou OpenAPI : les modèles du SDK doivent matcher le schéma backend.

Les modèles Pydantic du SDK sont écrits à la main (contrairement au frontend qui
génère ses types depuis l'OpenAPI). Ce test rattache la main écriture au contrat :
il compare chaque modèle aux composants de `backend/openapi.json` (mêmes champs,
même caractère requis). Toute dérive backend non répercutée dans le SDK échoue ici.

`backend/openapi.json` est tenu à jour par un test côté backend
(`test_openapi_contract.py`) ; la boucle est donc fermée.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from architecto_sdk.models import (
    ChatRequest,
    ChatResponse,
    DecisionOut,
    IngestResult,
    ProjectOut,
    SourceOut,
)

OPENAPI = Path(__file__).resolve().parents[3] / "backend" / "openapi.json"

# Modèle SDK -> nom du composant OpenAPI correspondant.
# HealthStatus (réponse non typée côté backend) et ChatStreamEvent (flux SSE hors
# OpenAPI) n'ont pas de composant : non couverts par construction.
MODEL_TO_COMPONENT = {
    ChatRequest: "ChatRequest",
    ChatResponse: "ChatResponse",
    SourceOut: "SourceOut",
    IngestResult: "IngestResult",
    ProjectOut: "ProjectOut",
    DecisionOut: "DecisionOut",
}


@pytest.fixture(scope="module")
def components() -> dict:
    if not OPENAPI.exists():
        pytest.skip("backend/openapi.json indisponible (hors monorepo)")
    schema = json.loads(OPENAPI.read_text(encoding="utf-8"))
    return schema["components"]["schemas"]


@pytest.mark.parametrize(
    ("model", "component_name"),
    [(m, c) for m, c in MODEL_TO_COMPONENT.items()],
    ids=[c for c in MODEL_TO_COMPONENT.values()],
)
def test_modele_sdk_conforme_au_composant_openapi(model, component_name, components):
    assert component_name in components, (
        f"Composant '{component_name}' absent de l'OpenAPI : "
        "l'endpoint a peut-être disparu ou été renommé côté backend."
    )
    component = components[component_name]
    schema_fields = set(component.get("properties", {}))
    schema_required = set(component.get("required", []))

    sdk_fields = set(model.model_fields)
    sdk_required = {n for n, f in model.model_fields.items() if f.is_required()}

    assert sdk_fields == schema_fields, (
        f"{model.__name__} : champs désalignés du schéma '{component_name}'. "
        f"En trop : {sdk_fields - schema_fields or '∅'} ; "
        f"manquants : {schema_fields - sdk_fields or '∅'}."
    )
    assert sdk_required == schema_required, (
        f"{model.__name__} : caractère requis désaligné. "
        f"Requis SDK : {sdk_required} ; requis schéma : {schema_required}."
    )
