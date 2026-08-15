import { beforeEach, describe, expect, it, vi } from "vitest";

// On mocke le client réseau : les tests pilotent le flux via les handlers.
vi.mock("@/api/client", () => ({ streamChat: vi.fn() }));

import { streamChat } from "@/api/client";
import { ChatStore } from "@/stores/ChatStore";

const mockStream = vi.mocked(streamChat);

beforeEach(() => {
  localStorage.clear();
  mockStream.mockReset();
});

describe("ChatStore — gestion des conversations", () => {
  it("démarre avec une conversation vide et active", () => {
    const s = new ChatStore();
    expect(s.conversations).toHaveLength(1);
    expect(s.messages).toHaveLength(0);
    expect(s.activeId).toBe(s.conversations[0].id);
  });

  it("newConversation ajoute en tête et l'active", () => {
    const s = new ChatStore();
    const firstId = s.activeId;
    s.newConversation();
    expect(s.conversations).toHaveLength(2);
    expect(s.conversations[0].id).toBe(s.activeId);
    expect(s.activeId).not.toBe(firstId);
  });

  it("selectConversation change la conversation active", () => {
    const s = new ChatStore();
    const firstId = s.activeId;
    s.newConversation();
    s.selectConversation(firstId);
    expect(s.activeId).toBe(firstId);
  });

  it("deleteConversation retire, et garde toujours au moins une conversation", () => {
    const s = new ChatStore();
    s.newConversation();
    expect(s.conversations).toHaveLength(2);

    s.deleteConversation(s.activeId);
    expect(s.conversations).toHaveLength(1);

    // supprimer la dernière → une nouvelle conversation vide est recréée
    s.deleteConversation(s.activeId);
    expect(s.conversations).toHaveLength(1);
    expect(s.messages).toHaveLength(0);
  });

  it("setProject affecte le projet de la conversation active", () => {
    const s = new ChatStore();
    s.setProject("erp-hospitalier");
    expect(s.project).toBe("erp-hospitalier");
  });

  it("canSend : faux si vide ou espaces, vrai sinon", () => {
    const s = new ChatStore();
    expect(s.canSend).toBe(false);
    s.setInput("   ");
    expect(s.canSend).toBe(false);
    s.setInput("bonjour");
    expect(s.canSend).toBe(true);
  });
});

describe("ChatStore — send (flux mocké)", () => {
  it("remplit la bulle assistant au fil des deltas + titre depuis le 1er message", async () => {
    mockStream.mockImplementation(async (_msg, _id, _proj, handlers) => {
      handlers?.onDelta("Bon");
      handlers?.onDelta("jour");
    });

    const s = new ChatStore();
    s.setInput("Ma question");
    await s.send();

    expect(s.messages).toHaveLength(2);
    expect(s.messages[0]).toMatchObject({ role: "user", content: "Ma question" });
    expect(s.messages[1]).toMatchObject({ role: "assistant", content: "Bonjour" });
    expect(s.active.title).toBe("Ma question");
    expect(s.input).toBe("");
    expect(s.loading).toBe(false);
  });

  it("expose l'activité d'outil pendant le flux, effacée dès le premier token", async () => {
    const s = new ChatStore();
    let activityPendantOutil = "";

    mockStream.mockImplementation(async (_m, _i, _p, handlers) => {
      handlers?.onTool?.("generate_diagram", "start");
      activityPendantOutil = s.activity; // lu après le start
      handlers?.onDelta("Voici"); // du texte → efface l'activité
    });

    s.setInput("diagramme");
    await s.send();

    expect(activityPendantOutil).toBe("Génère un diagramme");
    expect(s.activity).toBe(""); // effacée en fin de flux
  });

  it("un flux sans contenu ne laisse pas de bulle assistant vide", async () => {
    mockStream.mockImplementation(async () => {
      /* aucun delta */
    });

    const s = new ChatStore();
    s.setInput("Hello");
    await s.send();

    expect(s.messages).toHaveLength(1);
    expect(s.messages[0].role).toBe("user");
  });

  it("une erreur sans contenu produit un message d'erreur", async () => {
    mockStream.mockImplementation(async (_m, _i, _p, handlers) => {
      handlers?.onError?.(new Error("backend injoignable"));
    });

    const s = new ChatStore();
    s.setInput("Hello");
    await s.send();

    const last = s.messages.at(-1)!;
    expect(last.role).toBe("error");
    expect(last.content).toContain("backend injoignable");
  });

  it("ne renvoie pas si l'entrée est vide", async () => {
    const s = new ChatStore();
    s.setInput("   ");
    await s.send();
    expect(mockStream).not.toHaveBeenCalled();
    expect(s.messages).toHaveLength(0);
  });

  it("sendText envoie le texte fourni (suggestions)", async () => {
    mockStream.mockImplementation(async (_m, _i, _p, h) => h?.onDelta("ok"));
    const s = new ChatStore();
    await s.sendText("Prompt exemple");
    expect(s.messages[0]).toMatchObject({ role: "user", content: "Prompt exemple" });
    expect(s.active.title).toBe("Prompt exemple");
  });

  it("regenerate remplace la dernière réponse pour le même message user", async () => {
    mockStream.mockImplementation(async (_m, _i, _p, h) => h?.onDelta("v1"));
    const s = new ChatStore();
    s.setInput("Question");
    await s.send();
    expect(s.messages.at(-1)?.content).toBe("v1");

    mockStream.mockImplementation(async (_m, _i, _p, h) => h?.onDelta("v2"));
    await s.regenerate();

    expect(s.messages).toHaveLength(2); // 1 user + 1 assistant (régénérée)
    expect(s.messages[0]).toMatchObject({ role: "user", content: "Question" });
    expect(s.messages.at(-1)?.content).toBe("v2");
  });
});
