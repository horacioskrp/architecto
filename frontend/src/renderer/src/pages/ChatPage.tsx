import { useEffect, useRef } from "react";
import { observer } from "mobx-react-lite";

import { Composer } from "@/components/chat/Composer";
import { Markdown } from "@/components/markdown/Markdown";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

export const ChatPage = observer(function ChatPage() {
  const { chat } = useStores();
  const endRef = useRef<HTMLDivElement>(null);

  const count = chat.messages.length;
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [count, chat.loading, chat.activeId]);

  const empty = count === 0;
  const last = chat.messages[count - 1];
  // Indicateur d'attente : uniquement avant l'arrivée du premier token.
  const thinking = chat.loading && (!last || last.content.length === 0);

  return (
    <div className="flex h-full flex-col">
      <div className="scrollbar-thin flex-1 overflow-y-auto">
        {empty ? (
          <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center px-4 text-center">
            <span className="mb-4 text-4xl">🏛️</span>
            <h1 className="text-2xl font-semibold tracking-tight">
              Comment puis-je t'aider à concevoir ?
            </h1>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              Décris ton besoin d'architecture — diagrammes, ADR, choix de
              base de données, revue de dépendances. Associe un projet pour
              que je me souvienne de tes décisions.
            </p>
          </div>
        ) : (
          <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
            {chat.messages.map((m, i) => (
              <Message key={i} role={m.role} content={m.content} />
            ))}
            {thinking && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="size-2 animate-pulse rounded-full bg-clay" />
                Architecto réfléchit…
              </div>
            )}
            <div ref={endRef} />
          </div>
        )}
      </div>

      <Composer />
    </div>
  );
});

function Message({ role, content }: { role: string; content: string }) {
  if (role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-muted px-4 py-2.5 text-sm text-foreground">
          {content}
        </div>
      </div>
    );
  }

  if (role === "error") {
    return (
      <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
        {content}
      </div>
    );
  }

  return (
    <div className={cn("text-sm leading-relaxed")}>
      <Markdown content={content} />
    </div>
  );
}
