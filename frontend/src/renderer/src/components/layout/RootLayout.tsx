import { Outlet } from "react-router-dom";

import { ConversationSidebar } from "@/components/layout/ConversationSidebar";

export function RootLayout() {
  return (
    <div className="flex h-screen">
      <ConversationSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b">
          <div className="flex h-14 items-center px-4">
            <span className="text-base font-semibold">🏛️ Architecto</span>
            <span className="ml-2 text-sm text-muted-foreground">
              architecte logiciel IA
            </span>
          </div>
        </header>
        <main className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
