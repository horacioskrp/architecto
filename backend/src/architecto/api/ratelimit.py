from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable, Iterable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class SlidingWindowLimiter:
    """Compteur à fenêtre glissante par clé, en mémoire du process.

    Conserve les horodatages des requêtes récentes par clé (IP) ; une requête
    est autorisée tant que moins de `limit` requêtes tombent dans la fenêtre.
    """

    def __init__(self, limit: int, window: float) -> None:
        self._limit = limit
        self._window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        hits = self._hits[key]
        cutoff = now - self._window
        while hits and hits[0] <= cutoff:
            hits.popleft()
        if len(hits) >= self._limit:
            return False
        hits.append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Renvoie 429 au-delà de `limit` requêtes par `window_seconds` et par IP."""

    def __init__(
        self,
        app: Callable,
        *,
        limit: int,
        window_seconds: float,
        exempt_paths: Iterable[str] = (),
    ) -> None:
        super().__init__(app)
        self._limiter = SlidingWindowLimiter(limit, window_seconds)
        self._window = window_seconds
        self._exempt = set(exempt_paths)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in self._exempt:
            return await call_next(request)
        client = request.client.host if request.client else "?"
        if not self._limiter.allow(client):
            return JSONResponse(
                {"detail": "Trop de requêtes, réessayez plus tard."},
                status_code=429,
                headers={"Retry-After": str(int(self._window))},
            )
        return await call_next(request)
