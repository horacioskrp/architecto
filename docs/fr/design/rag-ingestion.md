# Design — Ingestion RAG

> 🇬🇧 [English version](../../en/design/rag-ingestion.md) · Feuille de route : [roadmap](../roadmap.md)

Note de conception de `feature/rag-ingestion`. La base pgvector est vide : l'outil
`search_knowledge_base` ne renvoie donc rien. Cette feature met en place le pipeline
qui l'alimente.

## Décisions

- **Interface** : script CLI d'abord (`scripts/ingest.py`). Endpoint API plus tard.
- **Idempotence** : *delete-by-source* — on trace chaque source dans la table
  `Document` (hash + nombre de chunks), on supprime ses anciens chunks avant de
  réinsérer. Idempotent par fichier, gère les fichiers rétrécis.
- **Formats** : `.md`, `.txt`, `.pdf`.

## Arborescence

```
features/knowledge/
├── models.py            # Document (étendu)
├── vectorstore.py       # get_vectorstore (existant)
├── tools.py             # search_knowledge_base (existant)
└── ingestion/
    ├── loaders.py       # lecture par extension (.md/.txt/.pdf) -> texte + titre
    ├── chunking.py      # découpe -> chunks (contenu + métadonnées)
    └── ingestor.py      # orchestration : load -> chunk -> upsert -> trace Document
backend/scripts/ingest.py   # CLI
```

## Modèle `Document` (étendu)

Sert de registre des sources ingérées (audit + idempotence) :

| Champ | Rôle |
|-------|------|
| `source` | Chemin/URL, **clé** d'une source |
| `title` | Titre (H1 Markdown ou nom de fichier) |
| `content_hash` | Hash du contenu → détecte l'inchangé |
| `chunk_count` | Nombre de chunks → permet de supprimer les anciens |
| `created_at` / `updated_at` | Audit |

## Idempotence (delete-by-source)

IDs de chunks **déterministes** : `f"{sha1(source)}:{i}"`.

1. Calculer le hash du fichier.
2. `Document` existe et `content_hash` identique → **skip** (ré-ingestion incrémentale).
3. `Document` existe et contenu changé → **supprimer** les ids `range(chunk_count)`,
   réinsérer, mettre à jour `Document`.
4. Source nouvelle → insérer + créer `Document`.

`--reset` → purge de la collection pgvector et de la table `documents` avant ingestion.

## Chunking & métadonnées

`RecursiveCharacterTextSplitter` (défaut `chunk_size=1000`, `overlap=150`).
Chaque chunk porte : `source`, `title`, `chunk_index`, `content_hash`.
→ **prépare la feature `rag-citations`** (les réponses pourront citer `source`/`title`).

## Embeddings & upsert

`get_vectorstore().add_texts(texts, metadatas, ids)` via l'adaptateur existant
(provider configurable openai/google), en batch.

## Interface CLI

```bash
uv run python scripts/ingest.py <fichier|dossier> [--reset] [--chunk-size N] [--chunk-overlap N]
```

Sortie récapitulative : fichiers traités / ignorés, chunks créés, durée.

## Tests (sans base de données)

- **chunking** : texte → chunks + métadonnées attendues (pur).
- **ingestor** : embeddings **mockés** + vectorstore **mocké** + repo `Document` mocké →
  vérifie `add_texts` (ids déterministes + métadonnées) et l'idempotence
  (2ᵉ passage inchangé = skip ; modifié = delete puis insert).

## Points d'attention

- `pypdf` ajouté aux dépendances backend → `uv.lock` régénéré.
- Colonnes ajoutées à `Document` : en dev on relance `scripts/init_db.py` (create_all
  sur base fraîche) ; pas de migration Alembic pour l'instant.
- PDF : gérer proprement les pages vides / PDF scannés sans texte (skip + warning).

## Étapes d'implémentation (petits pushes)

1. ✅ Note de design (ce document)
2. ✅ `Document` étendu + `init_db`
3. ✅ Loaders (`.md`/`.txt`/`.pdf`) + dépendance `pypdf` + test
4. ✅ Chunking + métadonnées + test
5. ✅ Ingestor (idempotence) + test (mocks)
6. ✅ CLI `scripts/ingest.py`
7. 🟦 PR vers `develop`
