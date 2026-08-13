# Tests en conditions réelles (e2e)

> 🇬🇧 [English version](../en/e2e.md)

Comment rejouer la chaîne réelle (base + embeddings + agent) en quelques commandes.

## Prérequis

- **Docker** (base pgvector).
- **`backend/.env`** avec un provider de chat (`LLM_*`, **avec crédit**) et un provider
  d'embeddings. Astuce : `EMBEDDING_PROVIDER=local` (fastembed) fonctionne **sans clé** —
  idéal si le chat est DeepSeek/Claude (pas d'API d'embeddings).
- Extras installés selon le provider :
  ```bash
  cd backend
  uv sync --extra dev --extra local          # + --extra deepseek si chat DeepSeek
  ```

## Procédure

```bash
docker compose up -d db                       # base pgvector
cd backend
uv run python scripts/init_db.py              # schéma + extension vector
uv run python scripts/ingest.py ../docs/fr    # alimente le RAG
uv run python scripts/smoke.py                # ingestion + recherche + 1 tour de chat
```

`smoke.py` affiche un récapitulatif des 3 étapes. Le tour de chat nécessite un provider
chat fonctionnel ; s'il échoue (clé/solde), il est **rapporté proprement** sans planter.

## Ce que ça valide

| Étape | Vérifie |
|-------|---------|
| `init_db` | schéma + extension `vector` |
| `ingest.py` | chunking + embeddings + upsert pgvector + **idempotence** |
| recherche | `search_knowledge_base` renvoie des extraits **sourcés** |
| chat | l'agent tourne et **appelle ses outils** (nécessite un chat avec crédit) |

## Surcharger le provider de chat sans toucher `.env`

Les variables d'environnement priment sur `.env`. Exemple DeepSeek (clé lue depuis `.env`) :

```powershell
$env:LLM_PROVIDER="deepseek"; $env:LLM_MODEL="deepseek-chat"
$env:LLM_BASE_URL="https://api.deepseek.com"
uv run python scripts/smoke.py
```

## Notes

- **Embeddings** : DeepSeek et Claude n'en fournissent pas → `EMBEDDING_PROVIDER=local`
  débloque le RAG sans clé (petit modèle ONNX téléchargé au 1ᵉʳ usage).
- La base garde ses données dans le volume `architecto_pgdata` (un `stop`/`start` les
  conserve). `scripts/ingest.py --reset` repart d'une collection propre.
