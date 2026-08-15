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
  onTool?: (name: string, phase: "start" | "end") => void;
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

      let evt: {
        type: string;
        text?: string;
        message?: string;
        name?: string;
        phase?: "start" | "end";
      };
      try {
        evt = JSON.parse(raw);
      } catch {
        continue;
      }
      if (evt.type === "delta" && evt.text) handlers.onDelta(evt.text);
      else if (evt.type === "tool" && evt.name && evt.phase) {
        handlers.onTool?.(evt.name, evt.phase);
      } else if (evt.type === "done") handlers.onDone?.();
      else if (evt.type === "error") {
        handlers.onError?.(new Error(evt.message ?? "Erreur inconnue"));
      }
    }
  }
}

// --- Base de connaissances (RAG) --------------------------------------------

export interface KnowledgeSource {
  source: string;
  title: string;
  chunk_count: number;
}

export interface IngestResult {
  processed: number;
  skipped_unchanged: number;
  skipped_empty: number;
  chunks: number;
  rejected: string[];
}

export async function ingestFiles(files: File[]): Promise<IngestResult> {
  const form = new FormData();
  for (const file of files) form.append("files", file, file.name);
  const res = await fetch(`${BASE}/knowledge/ingest`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Erreur ingestion : ${res.status} ${detail}`.trim());
  }
  return res.json() as Promise<IngestResult>;
}

export async function listSources(): Promise<KnowledgeSource[]> {
  const res = await fetch(`${BASE}/knowledge/sources`);
  if (!res.ok) throw new Error(`Erreur API : ${res.status}`);
  const data = (await res.json()) as { sources: KnowledgeSource[] };
  return data.sources;
}

export async function deleteSource(source: string): Promise<void> {
  const url = `${BASE}/knowledge/sources?source=${encodeURIComponent(source)}`;
  const res = await fetch(url, { method: "DELETE" });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Erreur suppression : ${res.status}`);
  }
}

// --- Mémoire : décisions d'architecture (ADR) -------------------------------

export interface DecisionProject {
  slug: string;
  name: string;
  decision_count: number;
}

export interface Decision {
  id: string;
  title: string;
  status: string;
  context: string;
  decision: string;
  consequences: string;
}

export async function listDecisionProjects(): Promise<DecisionProject[]> {
  const res = await fetch(`${BASE}/memory/projects`);
  if (!res.ok) throw new Error(`Erreur API : ${res.status}`);
  const data = (await res.json()) as { projects: DecisionProject[] };
  return data.projects;
}

export async function listDecisions(project: string): Promise<Decision[]> {
  const url = `${BASE}/memory/decisions?project=${encodeURIComponent(project)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Erreur API : ${res.status}`);
  const data = (await res.json()) as { decisions: Decision[] };
  return data.decisions;
}
