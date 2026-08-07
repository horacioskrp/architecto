# Design — Mémoire projet

> 🇬🇧 [English version](../../en/design/project-memory.md) · Feuille de route : [roadmap](../roadmap.md)

Note de conception de `feature/project-memory`. Objectif : l'agent **se souvient**
des décisions d'architecture d'un projet d'une session à l'autre. Dovetail avec
`generate_adr` (une décision stockée a les mêmes champs qu'un ADR).

## Décisions

- **Identité projet** : slug explicite en argument, **repli sur `thread_id`** si absent.
- **Accès** : outils explicites `save_decision` / `recall_decisions` (l'agent décide).
- **Récupération** : **SQL (récence) + sémantique (pgvector)** fusionnés par
  **reranking RRF** (Reciprocal Rank Fusion). Interface extensible vers un reranker
  plus fort (LLM/cross-encoder) plus tard.

## Modèle de données

- `Project` : `slug` (unique), `name`, timestamps.
- `ArchitectureDecision` : `project_id`, `title`, `status`, `context`, `decision`,
  `consequences`, timestamps (mêmes champs qu'un ADR).

## Architecture (ports / adaptateurs)

Même pattern que l'ingestion → cœur testable sans DB.

- `DecisionStore` (SQL, source de vérité) : `add`, `list_by_project`, `clear`.
- `DecisionIndex` (pgvector, collection `architecto_decisions`) : `add(decision)`,
  `search(project, query, k)` → ids classés par similarité.
- `resolve_project(slug, thread_id)` → slug si fourni, sinon thread_id, sinon `default`.
- `reciprocal_rank_fusion(rankings)` → fusion de listes de rangs (fonction pure).

## Outils exposés à l'agent

- `save_decision(title, context, decision, consequences, status, project="")` :
  persiste (SQL) **et** indexe (vecteur). `thread_id` récupéré via `RunnableConfig` injecté.
- `recall_decisions(query="", project="", k=5)` :
  - avec `query` → candidats **sémantiques** + **récence** → **RRF** → top-k ;
  - sans `query` → liste récente (SQL).

## Reranking (RRF)

Pour chaque liste classée, `score(id) += 1 / (K + rang)` (K≈60). On trie par score
décroissant. Combine similarité sémantique et récence sans modèle supplémentaire.

## Tests (sans base de données)

- `reciprocal_rank_fusion` : fusion pure (ordre attendu).
- `resolve_project` : slug > thread_id > default.
- outils `save`/`recall` avec `DecisionStore` **et** `DecisionIndex` mockés.

## Points d'attention

- Injection de `thread_id` via `RunnableConfig` dans les outils.
- L'indexation vectorielle des décisions consomme des embeddings (clé requise en e2e).
- Nouvelles tables → relancer `scripts/init_db.py` en dev.

## Étapes d'implémentation (petits pushes)

1. ✅ Note de design (ce document)
2. ✅ Modèles `Project` + `ArchitectureDecision` + `init_db`
3. ✅ Reranking RRF + `resolve_project` + tests
4. ✅ Ports + adaptateurs (SQL + pgvector décisions)
5. ✅ Outils `save_decision` / `recall_decisions` + tests (mocks)
6. ✅ Branchement agent + roadmap
7. 🟦 PR vers `develop`
