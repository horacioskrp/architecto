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
| Frontend     | React (Vite)                                                        |

## Architecture (monorepo)

```
architecto/
├── backend/     # API + agent LangGraph
├── frontend/    # UI React
└── docker-compose.yml   # Postgres + pgvector
```

## Démarrage rapide

### 1. Base de données

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
cp .env.example .env        # renseigner OPENAI_API_KEY, LANGSMITH_API_KEY...
uv sync
uv run alembic upgrade head
uv run uvicorn architecto.main:app --reload
```

API sur http://localhost:8000 · docs sur http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI sur http://localhost:5173
