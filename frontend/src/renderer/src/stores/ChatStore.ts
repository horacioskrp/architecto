import { makeAutoObservable, runInAction } from "mobx";

import { sendChat } from "@/api/client";

export type MessageRole = "user" | "assistant" | "error";

export interface Message {
  role: MessageRole;
  content: string;
}

export class ChatStore {
  messages: Message[] = [];
  input = "";
  loading = false;
  threadId = "default";

  constructor() {
    makeAutoObservable(this);
  }

  setInput(value: string) {
    this.input = value;
  }

  get canSend() {
    return this.input.trim().length > 0 && !this.loading;
  }

  async send() {
    const text = this.input.trim();
    if (!text || this.loading) return;

    this.messages.push({ role: "user", content: text });
    this.input = "";
    this.loading = true;

    try {
      const { answer } = await sendChat(text, this.threadId);
      runInAction(() => {
        this.messages.push({ role: "assistant", content: answer });
      });
    } catch (error) {
      runInAction(() => {
        this.messages.push({ role: "error", content: String(error) });
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
  }
}
