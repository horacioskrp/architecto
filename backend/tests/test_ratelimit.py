from fastapi import FastAPI
from fastapi.testclient import TestClient

from architecto.api.ratelimit import RateLimitMiddleware, SlidingWindowLimiter


def test_fenetre_glissante_par_cle():
    rl = SlidingWindowLimiter(limit=2, window=100.0)
    assert rl.allow("a", now=0)
    assert rl.allow("a", now=1)
    assert not rl.allow("a", now=2)  # 3e dans la fenêtre -> refus
    assert rl.allow("a", now=101)  # la 1re (t=0) est sortie de la fenêtre
    assert rl.allow("b", now=2)  # une autre clé est indépendante


def _app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware, limit=2, window_seconds=60, exempt_paths={"/health"}
    )

    @app.get("/ping")
    def ping() -> dict:
        return {"ok": True}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


def test_middleware_429_au_dela_de_la_limite():
    client = TestClient(_app())
    assert client.get("/ping").status_code == 200
    assert client.get("/ping").status_code == 200
    resp = client.get("/ping")
    assert resp.status_code == 429
    assert resp.headers.get("Retry-After") == "60"


def test_middleware_exempte_la_sante():
    client = TestClient(_app())
    for _ in range(5):
        assert client.get("/health").status_code == 200
