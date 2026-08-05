# Architecto — Backend

FastAPI + LangGraph + pgvector.

## Prérequis
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Postgres avec pgvector (via `docker compose up -d db` à la racine)

## Installation

```bash
cp .env.example .env      # renseigner OPENAI_API_KEY, LANGSMITH_API_KEY
uv sync
uv run python scripts/init_db.py
uv run uvicorn architecto.main:app --reload
```

- API : http://localhost:8000
- Docs OpenAPI : http://localhost:8000/docs
- Health : `GET /api/v1/health`
- Chat : `POST /api/v1/chat` — `{ "message": "...", "thread_id": "..." }`

## Arborescence

```
src/architecto/
├── main.py            # app FastAPI + CORS + LangSmith
├── api/v1/            # routes (health, chat)
├── agent/             # LangGraph : state, prompts, nodes, graph, tools/
├── core/
│   ├── config/       # settings par domaine (app, database, llm, observability, cors)
│   ├── env/          # résolution + cache du fichier .env
│   └── llm.py        # ChatOpenAI + embeddings
├── db/                # session async, models, vectorstore pgvector
└── schemas/           # DTO Pydantic
```

### Configuration

Tout passe par l'environnement, sans valeur métier en dur. Chaque section a son préfixe :
`APP_`, `DB_`, `LLM_`, `LANGSMITH_`, `CORS_` (voir `.env.example`). L'accès se fait
via `settings.<section>.<champ>` (ex. `settings.db.url`, `settings.llm.model`). Les
secrets sont des `SecretStr` et l'URL Postgres est composée à partir de ses composants.

## Notes production
- Remplacer `MemorySaver` par `AsyncPostgresSaver` (persistance des threads).
- Ajouter Alembic pour le versionnage de schéma.
- Streaming SSE via `app.astream_events` pour l'UI.
