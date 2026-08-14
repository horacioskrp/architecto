import type { Conversation } from "@/stores/ChatStore";

// Persistance locale (localStorage). Abstraite ici pour pouvoir passer à
// electron-store (via window.api) plus tard sans toucher au store.
const KEY = "architecto.conversations";

export function loadConversations(): Conversation[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const data: unknown = JSON.parse(raw);
    return Array.isArray(data) ? (data as Conversation[]) : [];
  } catch {
    return [];
  }
}

export function saveConversations(conversations: Conversation[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(conversations));
  } catch {
    // stockage indisponible : on ignore
  }
}
