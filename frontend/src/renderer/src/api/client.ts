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
