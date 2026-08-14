import { makeAutoObservable, reaction, runInAction } from "mobx";

import { sendChat } from "@/api/client";
import { loadConversations, saveConversations } from "@/lib/storage";

export type MessageRole = "user" | "assistant" | "error";

export interface Message {
  role: MessageRole;
  content: string;
}

export interface Conversation {
  id: string; // sert de thread_id backend
  title: string;
  project: string;
  messages: Message[];
}

function newId(): string {
  return globalThis.crypto?.randomUUID?.() ?? String(Date.now());
}

function emptyConversation(): Conversation {
  return { id: newId(), title: "Nouvelle conversation", project: "", messages: [] };
}

export class ChatStore {
  conversations: Conversation[] = [];
  activeId = "";
  input = "";
  loading = false;

  constructor() {
    const saved = loadConversations();
    if (saved.length > 0) {
      this.conversations = saved;
      this.activeId = saved[0].id;
    } else {
      const first = emptyConversation();
      this.conversations = [first];
      this.activeId = first.id;
    }

    makeAutoObservable(this);

    // Persistance : sauvegarde à chaque changement des conversations.
    reaction(
      () => JSON.stringify(this.conversations),
      () => saveConversations(this.conversations),
    );
  }

  get active(): Conversation {
    return (
      this.conversations.find((c) => c.id === this.activeId) ?? this.conversations[0]
    );
  }

  get messages(): Message[] {
    return this.active?.messages ?? [];
  }

  get project(): string {
    return this.active?.project ?? "";
  }

  get canSend(): boolean {
    return this.input.trim().length > 0 && !this.loading;
  }

  setInput(value: string): void {
    this.input = value;
  }

  setProject(slug: string): void {
    if (this.active) this.active.project = slug;
  }

  newConversation(): void {
    const conv = emptyConversation();
    this.conversations.unshift(conv);
    this.activeId = conv.id;
    this.input = "";
  }

  selectConversation(id: string): void {
    this.activeId = id;
    this.input = "";
  }

  deleteConversation(id: string): void {
    this.conversations = this.conversations.filter((c) => c.id !== id);
    if (this.conversations.length === 0) {
      this.conversations.push(emptyConversation());
    }
    if (!this.conversations.some((c) => c.id === this.activeId)) {
      this.activeId = this.conversations[0].id;
    }
  }

  async send(): Promise<void> {
    const text = this.input.trim();
    if (!text || this.loading) return;

    const conv = this.active;
    conv.messages.push({ role: "user", content: text });
    if (conv.messages.length === 1) {
      conv.title = text.length > 40 ? `${text.slice(0, 40)}…` : text;
    }
    this.input = "";
    this.loading = true;

    try {
      const { answer } = await sendChat(text, conv.id, conv.project);
      runInAction(() => {
        conv.messages.push({ role: "assistant", content: answer });
      });
    } catch (error) {
      runInAction(() => {
        conv.messages.push({ role: "error", content: String(error) });
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
  }
}
