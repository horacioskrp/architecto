import type { Conversation } from "@/stores/ChatStore";

// Persistance des conversations. Deux back-ends :
// - durable (Electron) : fichier JSON côté main process via `window.api.conversations`
//   (IPC). Pas de plafond ~5-10 Mo, survit au vidage du cache web.
// - repli : localStorage, pour le dev navigateur et les tests (pas d'IPC).
const KEY = "architecto.conversations";

interface ConversationsBridge {
  load(): Promise<unknown>;
  save(data: Conversation[]): Promise<void>;
}

/** Pont IPC durable si on tourne dans Electron, sinon `undefined`. */
function durableStore(): ConversationsBridge | undefined {
  return (globalThis as { api?: { conversations?: ConversationsBridge } }).api?.conversations;
}

function asConversations(data: unknown): Conversation[] {
  return Array.isArray(data) ? (data as Conversation[]) : [];
}

function loadLocal(): Conversation[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? asConversations(JSON.parse(raw)) : [];
  } catch {
    return [];
  }
}

function saveLocal(conversations: Conversation[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(conversations));
  } catch (error) {
    // Quota dépassé ou stockage indisponible : on le signale plutôt que de le
    // taire (l'historique pourrait être tronqué sans le durable).
    console.error("Persistance localStorage échouée", error);
  }
}

export async function loadConversations(): Promise<Conversation[]> {
  const durable = durableStore();
  if (!durable) return loadLocal();
  try {
    const stored = asConversations(await durable.load());
    if (stored.length > 0) return stored;
    // Rien en durable : migration unique d'un éventuel historique localStorage.
    const legacy = loadLocal();
    if (legacy.length > 0) await durable.save(legacy);
    return legacy;
  } catch (error) {
    console.error("Persistance durable indisponible, repli localStorage", error);
    return loadLocal();
  }
}

export async function saveConversations(conversations: Conversation[]): Promise<void> {
  const durable = durableStore();
  if (durable) {
    try {
      await durable.save(conversations);
      return;
    } catch (error) {
      console.error("Écriture durable échouée, repli localStorage", error);
    }
  }
  saveLocal(conversations);
}
