import { createHashRouter } from "react-router-dom";

import { RootLayout } from "@/components/layout/RootLayout";
import { ChatPage } from "@/pages/ChatPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

// HashRouter : en prod Electron charge la page en file://, où l'history routing
// (createBrowserRouter) ne fonctionne pas.
export const router = createHashRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <ChatPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
