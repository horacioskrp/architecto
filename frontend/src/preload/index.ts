import { contextBridge } from "electron";

/**
 * API minimale et typée exposée au renderer via contextBridge.
 * Point d'extension pour de futurs canaux IPC (réglages, fs restreint, etc.).
 * Ne jamais exposer Node ou ipcRenderer brut.
 */
const api = {
  platform: process.platform,
};

export type Api = typeof api;

if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
}
