# architecto-desktop

App **desktop Electron** d'Architecto (client léger). Le renderer est l'app React +
TypeScript ; le backend tourne séparément.

## Stack

Electron · electron-vite · React 18 · TypeScript · React Router · Tailwind CSS ·
shadcn/ui · MobX.

Gestionnaire de paquets : **pnpm** (épinglé via `packageManager` dans `package.json`).
Active-le avec corepack (fourni avec Node) :

```bash
corepack enable pnpm
```

## Développement

```bash
pnpm install
pnpm dev               # lance l'app Electron (HMR)
```

L'app appelle le backend en URL absolue : `http://localhost:8000` par défaut,
surchargeable au build via `VITE_API_BASE_URL`.

## Scripts

| Script | Rôle |
|--------|------|
| `pnpm dev` | Lance l'app en développement (electron-vite, HMR) |
| `pnpm typecheck` | Vérifie les types (process node + web) |
| `pnpm build` | Typecheck + build des 3 process dans `out/` |
| `pnpm build:win` | Build + installeur Windows (electron-builder) |
| `pnpm build:mac` / `build:linux` | Installeurs macOS / Linux |

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
- pnpm bloque les scripts de build par défaut ; `electron` et `esbuild` sont
  autorisés dans `pnpm-workspace.yaml` (`allowBuilds`). Le `.npmrc`
  (`shamefully-hoist=true`) assure la compat electron-builder.
