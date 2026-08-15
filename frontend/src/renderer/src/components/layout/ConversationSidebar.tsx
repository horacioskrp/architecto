import { observer } from "mobx-react-lite";
import {
  FileText,
  Library,
  MessageSquarePlus,
  PanelLeftClose,
  Trash2,
} from "lucide-react";

import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

export const ConversationSidebar = observer(function ConversationSidebar() {
  const { chat, ui } = useStores();

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-border bg-sidebar">
      <div className="flex items-center justify-between px-4 py-3.5">
        <Logo className="h-5 w-auto" />
        <button
          type="button"
          onClick={() => ui.toggleSidebar()}
          className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          title="Fermer la barre latérale"
          aria-label="Fermer la barre latérale"
        >
          <PanelLeftClose className="size-4" />
        </button>
      </div>

      <div className="px-3 pb-2">
        <button
          type="button"
          onClick={() => chat.newConversation()}
          className="flex w-full items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent"
        >
          <MessageSquarePlus className="size-4" />
          Nouvelle conversation
        </button>
      </div>

      <nav className="scrollbar-thin flex-1 overflow-y-auto px-2 pb-2">
        <ul className="flex flex-col gap-0.5">
          {chat.conversations.map((c) => (
            <li key={c.id}>
              <div
                className={cn(
                  "group flex items-center gap-1 rounded-lg px-2.5 py-2 text-sm transition-colors",
                  c.id === chat.activeId
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
                )}
              >
                <button
                  type="button"
                  onClick={() => chat.selectConversation(c.id)}
                  className="flex min-w-0 flex-1 flex-col items-start text-left"
                  title={c.title}
                >
                  <span className="w-full truncate">{c.title}</span>
                  {c.project && (
                    <span className="w-full truncate text-[11px] text-muted-foreground">
                      {c.project}
                    </span>
                  )}
                </button>
                <button
                  type="button"
                  aria-label="Supprimer la conversation"
                  onClick={() => chat.deleteConversation(c.id)}
                  className="shrink-0 rounded p-1 text-muted-foreground opacity-0 transition hover:text-destructive focus:opacity-100 group-hover:opacity-100"
                >
                  <Trash2 className="size-3.5" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      </nav>

      <div className="flex flex-col border-t border-border p-2">
        <button
          type="button"
          onClick={() => ui.openKnowledge()}
          className="flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          title="Gérer les documents de la base de connaissances"
        >
          <Library className="size-4" />
          Base de connaissances
        </button>
        <button
          type="button"
          onClick={() => ui.openDecisions()}
          className="flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          title="Consulter les décisions d'architecture mémorisées"
        >
          <FileText className="size-4" />
          Décisions
        </button>
        <ThemeToggle />
      </div>
    </aside>
  );
});
