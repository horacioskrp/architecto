import { observer } from "mobx-react-lite";
import { PanelLeft } from "lucide-react";
import { Outlet } from "react-router-dom";

import { ConversationSidebar } from "@/components/layout/ConversationSidebar";
import { DecisionsModal } from "@/components/decisions/DecisionsModal";
import { KnowledgeModal } from "@/components/knowledge/KnowledgeModal";
import { useStores } from "@/stores/context";

export const RootLayout = observer(function RootLayout() {
  const { ui } = useStores();

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {ui.sidebarOpen && <ConversationSidebar />}
      <main className="relative flex min-w-0 flex-1 flex-col">
        {!ui.sidebarOpen && (
          <button
            type="button"
            onClick={() => ui.toggleSidebar()}
            className="absolute left-3 top-3 z-10 rounded-md border border-border bg-card/80 p-1.5 text-muted-foreground shadow-sm backdrop-blur transition-colors hover:bg-accent hover:text-foreground"
            title="Ouvrir la barre latérale"
            aria-label="Ouvrir la barre latérale"
          >
            <PanelLeft className="size-4" />
          </button>
        )}
        <Outlet />
      </main>
      <KnowledgeModal />
      <DecisionsModal />
    </div>
  );
});
