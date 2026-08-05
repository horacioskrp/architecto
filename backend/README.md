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
├── api/v1/            # agrégateur : inclut les routers des features
├── agent/             # orchestration LangGraph : state, prompts, nodes, graph, tools
├── core/              # fondations transverses (aucun métier)
│   ├── config/       # settings par domaine (app, database, llm, embeddings, observability, cors)
│   ├── env/          # résolution + cache du fichier .env
│   ├── db/           # infra connexion : base (DeclarativeBase) + session async
│   └── llm/          # adaptateurs multi-provider (Adapter + Registry)
│       ├── base.py       # ports ChatAdapter / EmbeddingAdapter
│       ├── registry.py   # get_chat_model() / get_embeddings()
│       └── providers/    # anthropic · openai · google · deepseek (imports paresseux)
└── features/          # vertical slices (métier regroupé par feature)
    ├── chat/         # router + schemas
    ├── knowledge/    # models · vectorstore pgvector · tool de recherche (RAG)
    └── health/       # router
```

> **Organisation** : `core/` = fondations transverses (connexion DB, config, LLM),
> `features/` = métier en tranches verticales (chaque feature possède son router,
> ses schémas, ses modèles et ses outils). L'agent est le moteur d'orchestration qui
> agrège les outils exposés par les features.

### Configuration

Tout passe par l'environnement, sans valeur métier en dur. Chaque section a son préfixe :
`APP_`, `DB_`, `LLM_`, `EMBEDDING_`, `LANGSMITH_`, `CORS_` (voir `.env.example`). L'accès se
fait via `settings.<section>.<champ>` (ex. `settings.db.url`, `settings.llm.model`). Les
secrets sont des `SecretStr` et l'URL Postgres est composée à partir de ses composants.

### LLM multi-provider (adaptateur)

Le provider est interchangeable par config, sans toucher au code :

- **chat** : `LLM_PROVIDER` ∈ `anthropic | openai | google | deepseek` (+ `LLM_MODEL`, `LLM_API_KEY`)
- **embeddings** : `EMBEDDING_PROVIDER` ∈ `openai | google` (découplé — Anthropic n'a pas d'embeddings)

Chaque adaptateur importe son intégration LangChain de façon paresseuse : la base installe
`anthropic` (chat par défaut) + `openai` (embeddings). Pour les autres :

```bash
uv add architecto[google]     # ou : uv add langchain-google-genai
uv add architecto[deepseek]   # ou : uv add langchain-deepseek
```

Ajouter un provider = un fichier dans `core/llm/providers/` qui s'enregistre via
`register_chat(...)` / `register_embedding(...)`.

## Notes production
- Remplacer `MemorySaver` par `AsyncPostgresSaver` (persistance des threads).
- Ajouter Alembic pour le versionnage de schéma.
- Streaming SSE via `app.astream_events` pour l'UI.
