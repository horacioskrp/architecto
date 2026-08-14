import { ChatStore } from "@/stores/ChatStore";
import { ThemeStore } from "@/stores/ThemeStore";

export class RootStore {
  chat: ChatStore;
  theme: ThemeStore;

  constructor() {
    this.chat = new ChatStore();
    this.theme = new ThemeStore();
  }
}
