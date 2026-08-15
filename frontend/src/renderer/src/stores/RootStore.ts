import { ChatStore } from "@/stores/ChatStore";
import { DecisionsStore } from "@/stores/DecisionsStore";
import { KnowledgeStore } from "@/stores/KnowledgeStore";
import { ThemeStore } from "@/stores/ThemeStore";
import { UiStore } from "@/stores/UiStore";

export class RootStore {
  chat: ChatStore;
  theme: ThemeStore;
  ui: UiStore;
  knowledge: KnowledgeStore;
  decisions: DecisionsStore;

  constructor() {
    this.chat = new ChatStore();
    this.theme = new ThemeStore();
    this.ui = new UiStore();
    this.knowledge = new KnowledgeStore();
    this.decisions = new DecisionsStore();
  }
}
