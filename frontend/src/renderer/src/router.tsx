import { createHashRouter } from "react-router-dom";

import { RouteErrorFallback } from "@/components/ErrorBoundary";
import { RootLayout } from "@/components/layout/RootLayout";
import { ChatPage } from "@/pages/ChatPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

// HashRouter : en prod Electron charge la page en file://, où l'history routing
// (createBrowserRouter) ne fonctionne pas.
export const router = createHashRouter([
  {
    path: "/",
    element: <RootLayout />,
    // Repli propre si une route jette : le data router intercepte l'erreur ici,
    // avant tout boundary React placé au-dessus de RouterProvider.
    errorElement: <RouteErrorFallback />,
    children: [
      { index: true, element: <ChatPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
