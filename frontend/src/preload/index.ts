import { contextBridge, ipcRenderer } from "electron";

/**
 * API minimale et typée exposée au renderer via contextBridge.
 * Point d'extension pour de futurs canaux IPC (réglages, fs restreint, etc.).
 * Ne jamais exposer Node ou ipcRenderer brut.
 */
const api = {
  platform: process.platform,
  // Persistance durable des conversations, côté main process (voir main/index.ts).
  conversations: {
    load: (): Promise<unknown> => ipcRenderer.invoke("conversations:load"),
    save: (data: unknown): Promise<void> => ipcRenderer.invoke("conversations:save", data),
  },
};

export type Api = typeof api;

if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
}
