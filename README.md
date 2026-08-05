# Architecto

**Architecto** est un agent IA « Software Architect » : il assiste la conception logicielle
(analyse de besoins, choix d'architecture, ADR, diagrammes, revue de code) en s'appuyant sur
une base de connaissances vectorielle.

📖 **Documentation** (FR / EN) : [`docs/`](docs/README.md)

## Stack

| Couche       | Technologies                                                        |
|--------------|---------------------------------------------------------------------|
| Backend      | FastAPI · uv · Pydantic v2                                          |
| Agent        | LangChain · LangGraph · LangSmith (observabilité)                  |
| Données      | PostgreSQL · pgvector (RAG) · SQLAlchemy · Alembic                 |
| Frontend     | React · TypeScript · Vite · React Router · Tailwind · shadcn/ui · MobX |

## Architecture (monorepo)

```
architecto/
├── backend/     # API + agent LangGraph
├── frontend/    # UI React
└── docker-compose.yml   # Postgres + pgvector
```

## Démarrage rapide

### Tout en Docker (le plus simple)

```bash
cp backend/.env.example backend/.env   # renseigner les clés LLM
docker compose up --build
```

Frontend : http://localhost:5173 · Backend : http://localhost:8000

### En local

```bash
docker compose up -d db                 # Postgres + pgvector (port 5433)
```

```bash
cd backend
cp .env.example .env                    # renseigner LLM_API_KEY, EMBEDDING_API_KEY...
uv sync
uv run python scripts/init_db.py        # extension vector + tables
uv run uvicorn architecto.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

API : http://localhost:8000/docs · UI : http://localhost:5173

📖 Détails : [`docs/`](docs/README.md) — [Démarrage](docs/fr/getting-started.md) · [Getting started](docs/en/getting-started.md)
