# architecto-desktop

App **desktop Electron** d'Architecto (client léger). Le renderer est l'app React +
TypeScript ; le backend tourne séparément.

## Stack

Electron · electron-vite · React 18 · TypeScript · React Router · Tailwind CSS ·
shadcn/ui · MobX.

Gestionnaire de paquets : **npm** (fourni avec Node).

## Développement

```bash
npm install
npm run dev            # lance l'app Electron (HMR)
```

L'app appelle le backend en URL absolue : `http://localhost:8000` par défaut,
surchargeable au build via `VITE_API_BASE_URL`.

## Scripts

| Script | Rôle |
|--------|------|
| `npm run dev` | Lance l'app en développement (electron-vite, HMR) |
| `npm run typecheck` | Vérifie les types (process node + web) |
| `npm run build` | Typecheck + build des 3 process dans `out/` |
| `npm run build:win` | Build + installeur Windows (electron-builder) |
| `npm run build:mac` / `build:linux` | Installeurs macOS / Linux |

## Structure

```
src/
├── main/index.ts       # process principal : fenêtre, cycle de vie, CSP prod
├── preload/index.ts    # pont typé (contextBridge -> window.api)
└── renderer/           # l'app React
    ├── index.html
    └── src/            # main.tsx · router.tsx · api · stores · components · pages
```

## Sécurité

`contextIsolation: true`, `sandbox: true`, `nodeIntegration: false`, preload minimal,
CSP stricte injectée en production (`script-src 'self'`).

## Notes

- Routage par `createHashRouter` (prod en `file://`).
- Preload en CommonJS (requis avec `sandbox: true`) — d'où l'absence de
  `"type": "module"` dans `package.json`.
- npm exécute les scripts de post-install par défaut (dont le téléchargement du
  binaire Electron) et aplatit `node_modules` — pas de config d'hoisting requise.
- Les surcharges de dépendances transitives (`nanoid`, `vite`) sont déclarées
  dans le champ `overrides` de `package.json`.
