import { useState } from "react";
import { sendChat } from "./api/client.js";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const { answer } = await sendChat(text);
      setMessages((m) => [...m, { role: "assistant", content: answer }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "error", content: String(err) }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontWeight: 600 }}>🏛️ Architecto</h1>
      <p style={{ opacity: 0.7 }}>Votre architecte logiciel IA.</p>

      <div style={{ display: "flex", flexDirection: "column", gap: 12, margin: "24px 0" }}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#2563eb" : "#1c1f26",
              color: m.role === "error" ? "#f87171" : "#e6e6e6",
              padding: "10px 14px",
              borderRadius: 12,
              maxWidth: "80%",
              whiteSpace: "pre-wrap",
            }}
          >
            {m.content}
          </div>
        ))}
        {loading && <div style={{ opacity: 0.6 }}>Architecto réfléchit…</div>}
      </div>

      <form onSubmit={handleSend} style={{ display: "flex", gap: 8 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Décris ton besoin d'architecture…"
          style={{
            flex: 1,
            padding: "12px 14px",
            borderRadius: 10,
            border: "1px solid #2b2f38",
            background: "#12151b",
            color: "#e6e6e6",
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "12px 20px",
            borderRadius: 10,
            border: "none",
            background: "#2563eb",
            color: "white",
            cursor: "pointer",
          }}
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
