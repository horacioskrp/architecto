// En Electron il n'y a pas de proxy nginx : on appelle le backend en URL absolue.
// Surchargeable au build via VITE_API_BASE_URL.
const API_HOST = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const BASE = `${API_HOST}/api/v1`;

export interface ChatResponse {
  thread_id: string;
  answer: string;
}

export async function sendChat(
  message: string,
  threadId = "default",
  project = "",
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId, project }),
  });
  if (!res.ok) {
    throw new Error(`Erreur API : ${res.status}`);
  }
  return res.json() as Promise<ChatResponse>;
}

export interface StreamHandlers {
  onDelta: (text: string) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Consomme le flux SSE de `/chat/stream` et relaie les deltas.
 * On lit le corps de la réponse manuellement : `EventSource` ne gère pas POST.
 */
export async function streamChat(
  message: string,
  threadId = "default",
  project = "",
  handlers: StreamHandlers = { onDelta: () => {} },
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId, project }),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`Erreur API : ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // Les trames SSE sont séparées par une ligne vide.
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);

      const line = frame.split("\n").find((l) => l.startsWith("data:"));
      if (!line) continue;
      const raw = line.slice(5).trim();
      if (!raw) continue;

      let evt: { type: string; text?: string; message?: string };
      try {
        evt = JSON.parse(raw);
      } catch {
        continue;
      }
      if (evt.type === "delta" && evt.text) handlers.onDelta(evt.text);
      else if (evt.type === "done") handlers.onDone?.();
      else if (evt.type === "error") {
        handlers.onError?.(new Error(evt.message ?? "Erreur inconnue"));
      }
    }
  }
}
