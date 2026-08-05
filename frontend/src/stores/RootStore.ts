import { ChatStore } from "@/stores/ChatStore";

export class RootStore {
  chat: ChatStore;

  constructor() {
    this.chat = new ChatStore();
  }
}
