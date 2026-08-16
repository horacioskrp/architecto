import { join } from "node:path";

import { electronApp, is, optimizer } from "@electron-toolkit/utils";
import { app, BrowserWindow, session, shell } from "electron";

import icon from "../../build/icon.png?asset";

// Backend appelé par le renderer (client léger). Surchargeable via l'env.
const API_ORIGIN = process.env["ARCHITECTO_API_ORIGIN"] ?? "http://localhost:8000";

function applyProductionCSP(): void {
  // CSP stricte en prod seulement : en dev, le HMR de Vite a besoin d'inline scripts.
  const csp = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self' data:",
    `connect-src 'self' ${API_ORIGIN}`,
  ].join("; ");

  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        "Content-Security-Policy": [csp],
      },
    });
  });
}

function createWindow(): void {
  const window = new BrowserWindow({
    width: 1100,
    height: 750,
    show: false,
    autoHideMenuBar: true,
    icon,
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      sandbox: true,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  window.on("ready-to-show", () => window.show());

  // Les liens externes s'ouvrent dans le navigateur, pas dans l'app.
  window.webContents.setWindowOpenHandler(({ url }) => {
    void shell.openExternal(url);
    return { action: "deny" };
  });

  // Dev : serveur Vite (HMR). Prod : fichier buildé.
  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    void window.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    void window.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

void app.whenReady().then(() => {
  electronApp.setAppUserModelId("com.architecto.app");

  if (!is.dev) {
    applyProductionCSP();
  }

  app.on("browser-window-created", (_event, window) => {
    optimizer.watchWindowShortcuts(window);
  });

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
