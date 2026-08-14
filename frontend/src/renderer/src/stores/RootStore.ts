import { ChatStore } from "@/stores/ChatStore";
import { ThemeStore } from "@/stores/ThemeStore";
import { UiStore } from "@/stores/UiStore";

export class RootStore {
  chat: ChatStore;
  theme: ThemeStore;
  ui: UiStore;

  constructor() {
    this.chat = new ChatStore();
    this.theme = new ThemeStore();
    this.ui = new UiStore();
  }
}
