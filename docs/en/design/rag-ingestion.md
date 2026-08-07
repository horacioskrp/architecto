# Design — RAG ingestion

> 🇫🇷 [Version française](../../fr/design/rag-ingestion.md) · Roadmap: [roadmap](../roadmap.md)

Design note for `feature/rag-ingestion`. The pgvector store is empty, so
`search_knowledge_base` returns nothing. This feature builds the pipeline that
populates it.

## Decisions

- **Interface**: CLI script first (`scripts/ingest.py`). API endpoint later.
- **Idempotence**: *delete-by-source* — each source is tracked in the `Document`
  table (hash + chunk count); its old chunks are deleted before re-inserting.
  Idempotent per file, handles shrinking files.
- **Formats**: `.md`, `.txt`, `.pdf`.

## Layout

```
features/knowledge/
├── models.py            # Document (extended)
├── vectorstore.py       # get_vectorstore (existing)
├── tools.py             # search_knowledge_base (existing)
└── ingestion/
    ├── loaders.py       # per-extension reading (.md/.txt/.pdf) -> text + title
    ├── chunking.py      # split -> chunks (content + metadata)
    └── ingestor.py      # orchestration: load -> chunk -> upsert -> track Document
backend/scripts/ingest.py   # CLI
```

## `Document` model (extended)

Acts as a registry of ingested sources (audit + idempotence):

| Field | Purpose |
|-------|---------|
| `source` | Path/URL, **key** of a source |
| `title` | Title (Markdown H1 or file name) |
| `content_hash` | Content hash → detects unchanged files |
| `chunk_count` | Number of chunks → lets us delete old ones |
| `created_at` / `updated_at` | Audit |

## Idempotence (delete-by-source)

**Deterministic** chunk IDs: `f"{sha1(source)}:{i}"`.

1. Compute the file hash.
2. `Document` exists and `content_hash` unchanged → **skip** (incremental re-ingest).
3. `Document` exists and content changed → **delete** ids `range(chunk_count)`,
   re-insert, update `Document`.
4. New source → insert + create `Document`.

`--reset` → wipe the pgvector collection and the `documents` table before ingesting.

## Chunking & metadata

`RecursiveCharacterTextSplitter` (default `chunk_size=1000`, `overlap=150`).
Each chunk carries: `source`, `title`, `chunk_index`, `content_hash`.
→ **prepares `rag-citations`** (answers will be able to cite `source`/`title`).

## Embeddings & upsert

`get_vectorstore().add_texts(texts, metadatas, ids)` via the existing adapter
(configurable openai/google provider), batched.

## CLI

```bash
uv run python scripts/ingest.py <file|dir> [--reset] [--chunk-size N] [--chunk-overlap N]
```

Summary output: files processed / skipped, chunks created, duration.

## Tests (no database)

- **chunking**: text → chunks + expected metadata (pure).
- **ingestor**: **mocked** embeddings + **mocked** vectorstore + mocked `Document`
  repo → asserts `add_texts` (deterministic ids + metadata) and idempotence
  (2nd unchanged pass = skip; changed = delete then insert).

## Watch-outs

- `pypdf` added to backend deps → `uv.lock` regenerated.
- Columns added to `Document`: in dev re-run `scripts/init_db.py` (create_all on a
  fresh DB); no Alembic migration yet.
- PDF: handle empty pages / scanned PDFs without text (skip + warning).

## Implementation steps (small pushes)

1. ✅ Design note (this document)
2. ⬜ Extended `Document` + `init_db`
3. ⬜ Loaders (`.md`/`.txt`/`.pdf`) + `pypdf` dependency + test
4. ⬜ Chunking + metadata + test
5. ⬜ Ingestor (idempotence) + test (mocks)
6. ⬜ CLI `scripts/ingest.py`
7. ⬜ PR to `develop`
