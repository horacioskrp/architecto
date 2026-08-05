# Démarrage

> 🇬🇧 [English version](../en/getting-started.md)

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Docker (pour Postgres + pgvector)

## 1. Base de données

Postgres avec pgvector, exposé sur le port hôte **5433** (pour éviter tout conflit
avec un Postgres local sur 5432) :

```bash
docker compose up -d db
```

## 2. Backend

```bash
cd backend
cp .env.example .env        # renseigner les clés (LLM_API_KEY, EMBEDDING_API_KEY…)
uv sync
uv run python scripts/init_db.py     # extension vector + tables
uv run uvicorn architecto.main:app --reload
```

- API : http://localhost:8000
- Docs OpenAPI : http://localhost:8000/docs
- Health : `GET /api/v1/health`

Tester le chat :

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Propose une architecture pour une API de réservation", "thread_id": "demo"}'
```

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI : http://localhost:5173 (le proxy `/api` pointe vers le backend).

## Providers optionnels

La base installe Anthropic (chat) et OpenAI (embeddings). Pour Gemini ou DeepSeek :

```bash
uv add langchain-google-genai     # Gemini
uv add langchain-deepseek         # DeepSeek
```

Puis changer `LLM_PROVIDER` dans `.env`. Voir [Providers LLM](llm-providers.md).

## Dépannage

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| `Intégration manquante pour le provider …` | package du provider non installé | `uv add langchain-<provider>` |
| Connexion DB refusée | conteneur non démarré / mauvais port | `docker compose up -d db`, vérifier `DB_PORT=5433` |
| 401 côté LLM | clé API absente/incorrecte | renseigner `LLM_API_KEY` dans `.env` |
