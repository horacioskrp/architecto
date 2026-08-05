import { createBrowserRouter } from "react-router-dom";

import { RootLayout } from "@/components/layout/RootLayout";
import { ChatPage } from "@/pages/ChatPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <ChatPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
