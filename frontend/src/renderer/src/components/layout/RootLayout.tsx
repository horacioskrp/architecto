import { Outlet } from "react-router-dom";

import { ConversationSidebar } from "@/components/layout/ConversationSidebar";

export function RootLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <ConversationSidebar />
      <main className="flex min-w-0 flex-1 flex-col">
        <Outlet />
      </main>
    </div>
  );
}
