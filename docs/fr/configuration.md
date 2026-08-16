# Configuration

> 🇬🇧 [English version](../en/configuration.md)

Toute la configuration passe par des **variables d'environnement**, sans valeur
métier en dur. Elle est organisée par **sections de domaine**, chacune avec son
préfixe. Fichier de référence : [`backend/.env.example`](../../backend/.env.example).

## Principe

- Chaque section est un `BaseSettings` autonome avec son `env_prefix`.
- Les secrets sont des `SecretStr` (masqués dans les logs).
- L'accès se fait via `settings.<section>.<champ>` (ex. `settings.db.url`).
- Le fichier `.env` est résolu **une seule fois** par process (remontée
  d'arborescence + cache), indépendamment du répertoire courant.

## Sections

### `APP_` — application

| Variable | Défaut | Description |
|----------|--------|-------------|
| `APP_NAME` | `Architecto` | Nom de l'application |
| `APP_ENV` | `dev` | `dev` \| `staging` \| `prod` |
| `APP_DEBUG` | `false` | Mode debug FastAPI |
| `APP_API_V1_PREFIX` | `/api/v1` | Préfixe des routes |
| `APP_HOST` | `0.0.0.0` | Hôte d'écoute |
| `APP_PORT` | `8000` | Port d'écoute |

### `AGENT_` — comportement de l'agent

| Variable | Défaut | Description |
|----------|--------|-------------|
| `AGENT_CHECKPOINTER` | `memory` | Persistance des threads LangGraph : `memory` (volatil, dev/tests) \| `postgres` (durable via `AsyncPostgresSaver`, recommandé en prod) |

### `DB_` — base de données

L'URL Postgres est **composée** à partir des composants (rien en dur).

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DB_DRIVER` | `postgresql+psycopg` | Driver SQLAlchemy |
| `DB_HOST` | `localhost` | Hôte |
| `DB_PORT` | `5433` | Port (5433 pour éviter un conflit local) |
| `DB_USER` | `architecto` | Utilisateur |
| `DB_PASSWORD` | `architecto` | Mot de passe (`SecretStr`) |
| `DB_NAME` | `architecto` | Base |
| `DB_ECHO` | `false` | Log SQL |
| `DB_POOL_SIZE` | `5` | Taille du pool |
| `DB_MAX_OVERFLOW` | `10` | Connexions au-delà du pool |
| `DB_POOL_PRE_PING` | `true` | Vérifie la connexion avant usage |

### `LLM_` — modèle de chat

Voir [Providers LLM](llm-providers.md) pour le détail par provider.

| Variable | Défaut | Description |
|----------|--------|-------------|
| `LLM_PROVIDER` | `anthropic` | `anthropic` \| `openai` \| `google` \| `deepseek` |
| `LLM_MODEL` | `claude-sonnet-5` | Identifiant du modèle |
| `LLM_API_KEY` | — | Clé du provider (`SecretStr`) |
| `LLM_TEMPERATURE` | `0.2` | Température |
| `LLM_MAX_TOKENS` | — | Limite de tokens en sortie |
| `LLM_TIMEOUT` | `60` | Timeout (s) |
| `LLM_BASE_URL` | — | URL custom (DeepSeek, proxies OpenAI-compatibles) |

### `EMBEDDING_` — embeddings (RAG)

Découplé du chat : Anthropic ne fournit pas d'embeddings.

| Variable | Défaut | Description |
|----------|--------|-------------|
| `EMBEDDING_PROVIDER` | `openai` | `openai` \| `google` \| `local` (fastembed, **sans clé**) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Modèle d'embeddings |
| `EMBEDDING_API_KEY` | — | Clé (`SecretStr`) — inutile pour `local` |
| `EMBEDDING_BASE_URL` | — | URL custom |

### `KNOWLEDGE_` — ingestion de la base de connaissances

Garde-fous appliqués aux téléversements côté client (endpoint `/knowledge/ingest`).

| Variable | Défaut | Description |
|----------|--------|-------------|
| `KNOWLEDGE_MAX_UPLOAD_MB` | `20` | Taille max par fichier (Mo) |
| `KNOWLEDGE_MAX_FILES` | `20` | Nombre max de fichiers par requête |

### `LANGSMITH_` — observabilité

| Variable | Défaut | Description |
|----------|--------|-------------|
| `LANGSMITH_TRACING` | `false` | Active le tracing |
| `LANGSMITH_API_KEY` | — | Clé (`SecretStr`) |
| `LANGSMITH_PROJECT` | `architecto` | Nom du projet |
| `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` | Endpoint |

### `CORS_` — CORS

| Variable | Défaut | Description |
|----------|--------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173` | Origines autorisées (séparées par des virgules) |
| `CORS_ALLOW_CREDENTIALS` | `true` | Autoriser les credentials |

## Surcharger le fichier `.env`

La variable `ENV_FILE` permet de pointer vers un autre fichier :

```bash
ENV_FILE=/chemin/vers/.env.prod uv run uvicorn architecto.main:app
```

## Ajouter une section

1. Créer `core/config/<section>.py` avec une classe `SectionSettings` + `env_prefix`.
2. L'ajouter à `Settings` dans `core/config/settings.py`.
3. L'exposer dans `core/config/__init__.py`.
4. Documenter ses variables ici (FR) et dans la page EN équivalente.
