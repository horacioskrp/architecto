from fastapi.testclient import TestClient

from architecto.main import app


def test_lifespan_memoire_demarre_et_repond():
    """Le lifespan par défaut (checkpointer mémoire) ne casse pas le démarrage."""
    with TestClient(app) as client:  # entre/sort du lifespan
        res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
