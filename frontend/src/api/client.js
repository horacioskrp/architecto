const BASE = "/api/v1";

export async function sendChat(message, threadId = "default") {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!res.ok) throw new Error(`Erreur API : ${res.status}`);
  return res.json();
}
