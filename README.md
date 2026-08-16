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
| Desktop      | Electron · React · TypeScript · Vite · React Router · Tailwind · shadcn/ui · MobX |

## Architecture (monorepo)

```
architecto/
├── backend/     # API + agent LangGraph
├── frontend/    # app desktop Electron (renderer React/TypeScript)
├── sdk/python/  # SDK client Python (architecto-sdk)
├── docs/        # documentation FR/EN
└── docker-compose.yml   # Postgres + pgvector + backend
```

## Démarrage rapide

### 1. Base + backend (Docker)

```bash
cp backend/.env.example backend/.env   # renseigner les clés LLM
docker compose up --build              # db + backend (API sur :8000)
```

*(ou en local : `docker compose up -d db` puis `cd backend && uv sync && uv run python scripts/init_db.py && uv run uvicorn architecto.main:app --reload`)*

### 2. App desktop (Electron)

```bash
cd frontend
corepack enable pnpm   # active pnpm (fourni avec Node)
pnpm install
pnpm dev               # lance l'app Electron (pointe sur http://localhost:8000)
```

API : http://localhost:8000/docs

📖 Détails : [`docs/`](docs/README.md) — [Démarrage](docs/fr/getting-started.md) · [Getting started](docs/en/getting-started.md)

## Contribuer & communauté

- [Guide de contribution](CONTRIBUTING.md) — conventions Gitflow, PR.
- [Code de conduite](CODE_OF_CONDUCT.md) — Contributor Covenant.
- [Politique de sécurité](SECURITY.md) — signaler une vulnérabilité (canal privé).

## Licence

Distribué sous licence **MIT** — voir [`LICENSE`](LICENSE).
