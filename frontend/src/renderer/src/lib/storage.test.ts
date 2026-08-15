import { beforeEach, describe, expect, it } from "vitest";

import { loadConversations, saveConversations } from "@/lib/storage";
import type { Conversation } from "@/stores/ChatStore";

beforeEach(() => localStorage.clear());

const sample: Conversation[] = [
  { id: "1", title: "Ma conv", project: "erp", messages: [] },
];

describe("storage (persistance localStorage)", () => {
  it("round-trip : ce qui est sauvegardé est rechargé à l'identique", () => {
    saveConversations(sample);
    expect(loadConversations()).toEqual(sample);
  });

  it("stockage vide → tableau vide", () => {
    expect(loadConversations()).toEqual([]);
  });

  it("JSON invalide → tableau vide (pas de crash)", () => {
    localStorage.setItem("architecto.conversations", "{pas du json");
    expect(loadConversations()).toEqual([]);
  });

  it("valeur non-tableau → tableau vide", () => {
    localStorage.setItem("architecto.conversations", '{"a":1}');
    expect(loadConversations()).toEqual([]);
  });
});
