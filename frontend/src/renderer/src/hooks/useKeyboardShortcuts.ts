import { useEffect } from "react";

import { useStores } from "@/stores/context";

/**
 * Raccourcis clavier globaux :
 * - Ctrl/Cmd+N  → nouvelle conversation
 * - Ctrl/Cmd+K  → focus sur la zone de saisie
 * - Échap       → arrête le streaming en cours
 */
export function useKeyboardShortcuts(): void {
  const { chat } = useStores();

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;

      if (mod && e.key.toLowerCase() === "n") {
        e.preventDefault();
        chat.newConversation();
        focusComposer();
        return;
      }

      if (mod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        focusComposer();
        return;
      }

      if (e.key === "Escape" && chat.loading) {
        chat.stop();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [chat]);
}

function focusComposer(): void {
  const el = document.querySelector<HTMLTextAreaElement>('[aria-label="Message"]');
  el?.focus();
}
