const BASE = "/api/v1";

export interface ChatResponse {
  thread_id: string;
  answer: string;
}

export async function sendChat(
  message: string,
  threadId = "default",
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!res.ok) {
    throw new Error(`Erreur API : ${res.status}`);
  }
  return res.json() as Promise<ChatResponse>;
}
