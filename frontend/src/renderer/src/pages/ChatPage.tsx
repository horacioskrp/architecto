import { type FormEvent } from "react";
import { observer } from "mobx-react-lite";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

export const ChatPage = observer(function ChatPage() {
  const { chat } = useStores();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    void chat.send();
  }

  return (
    <div className="flex flex-col gap-4">
      {chat.messages.length === 0 && (
        <p className="py-10 text-center text-sm text-muted-foreground">
          Décris ton besoin d'architecture pour démarrer la conversation.
        </p>
      )}

      <div className="flex flex-col gap-3">
        {chat.messages.map((m, i) => (
          <div
            key={i}
            className={cn(
              "max-w-[80%] whitespace-pre-wrap rounded-lg px-4 py-2 text-sm",
              m.role === "user" &&
                "self-end bg-primary text-primary-foreground",
              m.role === "assistant" && "self-start bg-muted",
              m.role === "error" &&
                "self-start bg-destructive/10 text-destructive",
            )}
          >
            {m.content}
          </div>
        ))}
        {chat.loading && (
          <div className="self-start text-sm text-muted-foreground">
            Architecto réfléchit…
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={chat.input}
          onChange={(e) => chat.setInput(e.target.value)}
          placeholder="Décris ton besoin d'architecture…"
          aria-label="Message"
        />
        <Button type="submit" disabled={!chat.canSend}>
          Envoyer
        </Button>
      </form>
    </div>
  );
});
