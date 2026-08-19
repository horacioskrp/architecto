import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { loadConversations, saveConversations } from "@/lib/storage";
import type { Conversation } from "@/stores/ChatStore";

beforeEach(() => localStorage.clear());
afterEach(() => {
  delete (globalThis as { api?: unknown }).api;
});

const sample: Conversation[] = [
  { id: "1", title: "Ma conv", project: "erp", messages: [] },
];

describe("storage — repli localStorage (pas d'IPC)", () => {
  it("round-trip : ce qui est sauvegardé est rechargé à l'identique", async () => {
    await saveConversations(sample);
    expect(await loadConversations()).toEqual(sample);
  });

  it("stockage vide → tableau vide", async () => {
    expect(await loadConversations()).toEqual([]);
  });

  it("JSON invalide → tableau vide (pas de crash)", async () => {
    localStorage.setItem("architecto.conversations", "{pas du json");
    expect(await loadConversations()).toEqual([]);
  });

  it("valeur non-tableau → tableau vide", async () => {
    localStorage.setItem("architecto.conversations", '{"a":1}');
    expect(await loadConversations()).toEqual([]);
  });
});

describe("storage — back-end durable (Electron/IPC simulé)", () => {
  it("utilise le pont durable en priorité pour lire et écrire", async () => {
    const load = vi.fn().mockResolvedValue(sample);
    const save = vi.fn().mockResolvedValue(undefined);
    (globalThis as { api?: unknown }).api = { conversations: { load, save } };

    await saveConversations(sample);
    expect(save).toHaveBeenCalledWith(sample);

    expect(await loadConversations()).toEqual(sample);
    expect(load).toHaveBeenCalled();
    // Le durable étant disponible et non vide, localStorage n'est pas touché.
    expect(localStorage.getItem("architecto.conversations")).toBeNull();
  });

  it("migre l'historique localStorage vers le durable au premier chargement", async () => {
    localStorage.setItem("architecto.conversations", JSON.stringify(sample));
    const save = vi.fn().mockResolvedValue(undefined);
    (globalThis as { api?: unknown }).api = {
      conversations: { load: vi.fn().mockResolvedValue([]), save },
    };

    const loaded = await loadConversations();
    expect(loaded).toEqual(sample);
    expect(save).toHaveBeenCalledWith(sample); // migration vers le durable
  });

  it("repli localStorage si le durable échoue", async () => {
    localStorage.setItem("architecto.conversations", JSON.stringify(sample));
    (globalThis as { api?: unknown }).api = {
      conversations: {
        load: vi.fn().mockRejectedValue(new Error("IPC KO")),
        save: vi.fn(),
      },
    };
    expect(await loadConversations()).toEqual(sample);
  });
});
