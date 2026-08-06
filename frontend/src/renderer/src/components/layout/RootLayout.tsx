import { Outlet } from "react-router-dom";

export function RootLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="mx-auto flex h-14 max-w-3xl items-center px-4">
          <span className="text-base font-semibold">🏛️ Architecto</span>
          <span className="ml-2 text-sm text-muted-foreground">
            architecte logiciel IA
          </span>
        </div>
      </header>
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
