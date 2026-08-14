import { observer } from "mobx-react-lite";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

export const ConversationSidebar = observer(function ConversationSidebar() {
  const { chat } = useStores();

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r bg-muted/30">
      <div className="p-3">
        <Button className="w-full" onClick={() => chat.newConversation()}>
          + Nouvelle conversation
        </Button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-3">
        <ul className="flex flex-col gap-1">
          {chat.conversations.map((c) => (
            <li key={c.id}>
              <div
                className={cn(
                  "group flex items-center gap-1 rounded-md px-2 py-2 text-sm",
                  c.id === chat.activeId
                    ? "bg-primary/10 text-primary"
                    : "hover:bg-muted",
                )}
              >
                <button
                  type="button"
                  onClick={() => chat.selectConversation(c.id)}
                  className="min-w-0 flex-1 truncate text-left"
                  title={c.title}
                >
                  {c.title}
                  {c.project && (
                    <span className="ml-1 text-xs text-muted-foreground">
                      · {c.project}
                    </span>
                  )}
                </button>
                <button
                  type="button"
                  aria-label="Supprimer la conversation"
                  onClick={() => chat.deleteConversation(c.id)}
                  className="shrink-0 text-muted-foreground opacity-0 transition hover:text-destructive group-hover:opacity-100"
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
});
