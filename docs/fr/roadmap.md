# Feuille de route

> 🇬🇧 [English version](../en/roadmap.md)

Document de référence : ce qu'on construit, dans quel ordre, et comment on suit
l'avancement. Mis à jour à chaque PR mergée dans `develop`.

## Principes directeurs

- **Fiable avant large** : profondeur sur quelques capacités vérifiables plutôt que
  survol de beaucoup d'outils (éviter le *demoware*).
- **Artefacts éditables, pas d'oracle** : l'agent *drafte* des sorties relisibles
  (diagrammes, ADR, réponses citées) que l'humain valide.
- **Grounding** : séparer visiblement le **fait vérifié** (cité) de la **suggestion
  générée**.
- **Copilote, pas chatbot** : la valeur vient du raisonnement (clarification,
  compromis), pas d'une réponse autoritaire.

## Méthode de travail (Gitflow)

- Une capacité = une branche `feature/*` = une PR vers `develop`.
- Petites unités **testées** (au moins un test par feature).
- `develop` reste toujours intégrable ; `main` ne reçoit que des releases.
- Voir [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## Statut

Légende : ⬜ à faire · 🟦 en cours · ✅ fait

| Phase | Feature | Branche | Statut |
|-------|---------|---------|--------|
| 0 | CI + template PR | `feature/ci` | ⬜ |
| 1 | Boucle de clarification | `feature/clarify-loop` | ✅ |
| 1 | Ingestion RAG ([design](design/rag-ingestion.md)) | `feature/rag-ingestion` | ✅ |
| 1 | Réponses citées | `feature/rag-citations` | ✅ |
| 1 | Outil UML/Mermaid | `feature/uml-tool` | ✅ |
| 1 | Sortie ADR | `feature/adr-output` | ✅ |
| 2 | Mémoire projet ([design](design/project-memory.md)) | `feature/project-memory` | ✅ |
| 2 | Générateur d'architecture (compromis) | `feature/architecture-generator` | ✅ |
| 2 | Concepteur de base de données | `feature/database-designer` | ✅ |
| 3 | Analyseur de dépôt GitHub ([design](design/github-analyzer.md)) | `feature/github-analyzer` | ✅ |
| 3 | Checklist sécurité (OWASP) | `feature/security-checklist` | ✅ |
| Client | App Electron (client léger, markdown/mermaid) | `feature/electron-*` | ✅ |
| Client | Multi-conversations + historique persistant + projet | `feature/electron-phase-b` | ✅ |
| Client | Streaming des réponses (SSE) | `feature/electron-phase-c-streaming` | ✅ |
| Scale | Ingestion RAG depuis le client (upload) | `feature/knowledge-ingestion-ui` | ✅ |
| Scale | Transparence des outils (activité en direct) | `feature/tool-transparency` | ✅ |
| Scale | Persistance durable des threads (AsyncPostgresSaver) | `feature/durable-checkpointer` | ✅ |
| Scale | Panneau Décisions/ADR par projet | `feature/decisions-panel` | ✅ |
| Front | Robustesse : ErrorBoundary | `feature/frontend-error-boundary` | ✅ |
| Front | Types API générés depuis l'OpenAPI | `feature/frontend-openapi-types` | ✅ |
| Front | Tests Vitest (stores, ErrorBoundary, storage) | `feature/frontend-vitest` | ✅ |
| Front | Quick wins UX (suggestions, actions, raccourcis) | `feature/frontend-ux-quickwins` | ✅ |
| Front | Perf (lazy-load) + a11y (aria-live, focus-trap) | `feature/frontend-tier3` | ✅ |

---

## Phase 0 — Fondation (optionnelle, recommandée)

### `feature/ci`
- **Objectif** : valider chaque PR vers `develop` automatiquement.
- **Périmètre** : GitHub Actions — backend (`ruff` + `pytest` + `py_compile`),
  frontend (`tsc --noEmit` + `vite build`), sdk (`pytest`). Un
  `.github/pull_request_template.md`.
- **Acceptation** : le workflow s'exécute sur une PR et passe au vert.

## Phase 1 — Le trio crédible (fiable & démontrable)

### `feature/clarify-loop`
- **Objectif** : l'agent pose des questions quand des infos essentielles manquent,
  au lieu de répondre tout de suite.
- **Périmètre** : nœud `clarify` + edge conditionnel dans le graphe LangGraph ; état
  enrichi (`needs_clarification`, `questions`) ; politique de décision simple.
- **Livrables** : graphe mis à jour + test du routage.
- **Acceptation** : prompt vague → réponse contenant des questions ; prompt complet →
  pas de questions.

### `feature/rag-ingestion`
- **Objectif** : alimenter pgvector (le store est vide aujourd'hui).
- **Périmètre** : ingestion (chunking + embeddings + upsert) depuis des fichiers
  Markdown, via un script `scripts/ingest.py` (et/ou un endpoint).
- **Livrables** : script d'ingestion + test (embeddings mockés).
- **Acceptation** : après ingestion, `search_knowledge_base` renvoie des extraits
  pertinents.

### `feature/rag-citations`
- **Objectif** : chaque réponse ancrée cite ses sources.
- **Périmètre** : propager les métadonnées (titre/source) des chunks ; format de
  citation dans la réponse.
- **Livrables** : outil renvoyant contenu + source, prompt qui cite, test.
- **Acceptation** : une réponse RAG liste les sources utilisées.

### `feature/uml-tool`
- **Objectif** : générer des diagrammes Mermaid à partir d'une description.
- **Périmètre** : `@tool generate_diagram` (classe / séquence / composant) renvoyant
  du Mermaid valide.
- **Livrables** : outil + test (le bloc `mermaid` a la forme attendue).
- **Acceptation** : description → bloc ```mermaid``` cohérent.

### `feature/adr-output`
- **Objectif** : produire un ADR structuré.
- **Périmètre** : sortie/outil ADR (Contexte · Décision · Conséquences · Alternatives)
  au format Markdown.
- **Livrables** : outil + test de structure.
- **Acceptation** : sortie ADR avec les sections attendues.

## Phase 2 — Extension (semi-vérifiable, à ancrer)

- **`feature/project-memory`** — mémoire long terme : modèle `projets` + `décisions`
  (Postgres), retrouvés d'une session à l'autre.
- **`feature/architecture-generator`** — découpage modulaire **orienté compromis**
  (justifie les frontières et les couplages), pas une liste de modules.
- **`feature/database-designer`** — entités, relations, clés, index, script SQL ;
  validation **syntaxique** du SQL généré.

## Phase 3 — À ancrer (risque élevé sans grounding)

- **`feature/github-analyzer`** — **vraie** analyse de dépendances (graphe d'imports,
  règles de couches), pas une lecture LLM du repo.
- **`feature/security-checklist`** — checklist ancrée **OWASP** (une checklist, pas un
  verdict).

## Client & mise à l'échelle (post-Phase 3)

Une fois le trio backend crédible, l'effort s'est porté sur le **client desktop**
et la mise à l'échelle :

- **App Electron** (client léger) : rendu markdown + diagrammes mermaid,
  multi-conversations avec **historique persistant** (localStorage), sélection de
  projet, thème clair/sombre/système, et **streaming des réponses** token par
  token (SSE, endpoint `POST /chat/stream`).
- **Ingestion RAG depuis le client** : l'utilisateur téléverse ses propres
  documents (`.md`/`.txt`/`.pdf`) pour ancrer l'agent sur son contexte —
  endpoints `POST /knowledge/ingest`, `GET`/`DELETE /knowledge/sources`.
- **Transparence des outils** : le flux SSE relaie l'activité d'outil
  (« génère un diagramme… ») affichée en direct.
- **Persistance durable des threads** : `AsyncPostgresSaver` optionnel
  (`AGENT_CHECKPOINTER=postgres`), sinon checkpointer en mémoire.
- **Panneau Décisions/ADR** : consultation de la mémoire long terme par projet
  (endpoints `GET /memory/projects`, `GET /memory/decisions`).

### Robustesse frontend

- **ErrorBoundary** (global + par message) : un rendu défaillant n'efface plus l'app.
- **Types API générés depuis l'OpenAPI** (`openapi-typescript`) : source de vérité
  unique, fin de la dérive front/back — pipeline `scripts/dump_openapi.py` (back)
  puis `pnpm gen:api` (front).
- **Tests Vitest** : premiers tests des stores, de l'ErrorBoundary et de la persistance.
- **Perf** : lazy-load de mermaid et du syntax-highlighter (sortis du bundle initial).
- **A11y** : `aria-live` sur le streaming, piège de focus dans les modals.

> La **Phase 0 (CI)** reste à faire — d'autant plus pertinente maintenant que
> backend **et** frontend ont des tests à faire tourner sur chaque PR.

## Advisory — avec réserves explicites (jamais en sortie autoritaire)

- **Cost Estimator** et **Cloud Advisor** : disponibles en conversation, toujours
  assortis de réserves ; non ancrables de façon fiable → pas de sortie « officielle ».

## Différé

- **Multi-agents** (Architect / Database / Security / DevOps / Review / Docs) : on n'y
  passe que si un agent unique bien outillé ne suffit plus. Prématuré aujourd'hui.

## Hors périmètre (anti-objectifs)

- Pas de verdict autoritaire non ancré.
- Pas de multi-agents « pour la démo ».
- Pas de largeur au détriment de la profondeur du trio Phase 1.
