import { makeAutoObservable, reaction, runInAction, toJS } from "mobx";

import { streamChat } from "@/api/client";
import { loadConversations, saveConversations } from "@/lib/storage";
import { toolLabel } from "@/lib/toolLabels";

// Délai de debounce de la persistance. Pendant le streaming, le contenu est
// muté à chaque token ; sans debounce on réécrirait localStorage des centaines
// de fois par réponse. L'effet MobX `delay` ne s'exécute qu'après cette
// fenêtre d'inactivité, avec le dernier snapshot (état final garanti).
const PERSIST_DELAY_MS = 500;

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
  activity = ""; // libellé de l'outil en cours (transparence pendant le flux)
  private controller: AbortController | null = null;

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

    // Persistance debouncée : sauvegarde après une fenêtre d'inactivité, pas à
    // chaque token du flux. `toJS` produit un snapshot suivi en profondeur ;
    // l'écriture disque est différée à `PERSIST_DELAY_MS`.
    reaction(
      () => toJS(this.conversations),
      (snapshot) => saveConversations(snapshot),
      { delay: PERSIST_DELAY_MS },
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

  /** Interrompt le streaming en cours (le texte déjà reçu est conservé). */
  stop(): void {
    this.controller?.abort();
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
    await this.runStream(conv, text);
  }

  /** Envoie un texte donné (suggestions de l'état vide). */
  sendText(text: string): Promise<void> {
    this.input = text;
    return this.send();
  }

  /** Relance la génération depuis le dernier message utilisateur. */
  async regenerate(): Promise<void> {
    if (this.loading) return;
    const conv = this.active;
    const lastUser = [...conv.messages].reverse().find((m) => m.role === "user");
    if (!lastUser) return;
    // retire l'ancienne réponse (tout ce qui suit le dernier message utilisateur)
    conv.messages.splice(conv.messages.lastIndexOf(lastUser) + 1);
    await this.runStream(conv, lastUser.content);
  }

  private async runStream(conv: Conversation, text: string): Promise<void> {
    // Bulle assistant vide qu'on remplit au fil du flux (index stable).
    const idx = conv.messages.push({ role: "assistant", content: "" }) - 1;
    this.loading = true;
    this.controller = new AbortController();

    try {
      await streamChat(
        text,
        conv.id,
        conv.project,
        {
          onDelta: (t) => {
            runInAction(() => {
              this.activity = ""; // du texte arrive : l'outil n'est plus en cours
              conv.messages[idx].content += t;
            });
          },
          onTool: (name, phase) => {
            runInAction(() => {
              this.activity = phase === "start" ? toolLabel(name) : "";
            });
          },
          onError: (e) => {
            runInAction(() => {
              if (conv.messages[idx].content) {
                conv.messages[idx].content += `\n\n_(interrompu : ${e.message})_`;
              } else {
                conv.messages[idx].role = "error";
                conv.messages[idx].content = e.message;
              }
            });
          },
        },
        this.controller.signal,
      );
    } catch (error) {
      const aborted = error instanceof DOMException && error.name === "AbortError";
      runInAction(() => {
        if (aborted) {
          if (!conv.messages[idx].content) {
            conv.messages.splice(idx, 1);
          }
        } else if (conv.messages[idx].content) {
          conv.messages[idx].content += `\n\n_(interrompu : ${String(error)})_`;
        } else {
          conv.messages[idx].role = "error";
          conv.messages[idx].content = String(error);
        }
      });
    } finally {
      runInAction(() => {
        // Retire une bulle assistant restée vide (aucun token, pas d'erreur).
        if (
          conv.messages[idx]?.role === "assistant" &&
          !conv.messages[idx].content
        ) {
          conv.messages.splice(idx, 1);
        }
        this.activity = "";
        this.loading = false;
        this.controller = null;
      });
    }
  }
}
