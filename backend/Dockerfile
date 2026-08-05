# syntax=docker/dockerfile:1

# Base commune (même image pour builder et runtime → venv portable)
FROM python:3.12-slim-bookworm AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# ---- builder : installe les dépendances dans /app/.venv via uv ----
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Couche de cache : dépendances seules (sans le projet)
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# Le projet lui-même
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# ---- runtime : image minimale, utilisateur non-root ----
FROM base AS runtime
RUN useradd --create-home --uid 1000 app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["uvicorn", "architecto.main:app", "--host", "0.0.0.0", "--port", "8000"]
