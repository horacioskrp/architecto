import { type KeyboardEvent, useLayoutEffect, useRef } from "react";
import { observer } from "mobx-react-lite";
import { ArrowUp, FolderGit2, Square } from "lucide-react";

import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

const MAX_HEIGHT = 200;

export const Composer = observer(function Composer() {
  const { chat } = useStores();
  const areaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-agrandissement du textarea jusqu'à MAX_HEIGHT.
  useLayoutEffect(() => {
    const el = areaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, MAX_HEIGHT)}px`;
  }, [chat.input]);

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      void chat.send();
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-4">
      <div className="flex flex-col gap-2 rounded-[1.4rem] border border-border bg-card p-2.5 shadow-sm transition-colors focus-within:border-muted-foreground/40">
        <Textarea
          ref={areaRef}
          value={chat.input}
          onChange={(e) => chat.setInput(e.target.value)}
          onKeyDown={onKeyDown}
          rows={1}
          placeholder="Décris ton besoin d'architecture…"
          aria-label="Message"
          className="max-h-[200px] px-2 py-1.5 leading-6 scrollbar-thin"
        />

        <div className="flex items-center justify-between gap-2">
          <label
            className="group flex min-w-0 items-center gap-1.5 rounded-lg px-1.5 py-1 text-xs text-muted-foreground transition-colors focus-within:text-foreground hover:text-foreground"
            title="Projet associé — cadre la mémoire des décisions"
          >
            <FolderGit2 className="size-3.5 shrink-0" />
            <input
              value={chat.project}
              onChange={(e) => chat.setProject(e.target.value)}
              placeholder="projet"
              aria-label="Projet"
              className="w-24 min-w-0 bg-transparent placeholder:text-muted-foreground/60 focus:w-40 focus:outline-none"
            />
          </label>

          {chat.loading ? (
            <button
              type="button"
              onClick={() => chat.stop()}
              aria-label="Arrêter"
              className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <Square className="size-3.5 fill-current" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => void chat.send()}
              disabled={!chat.canSend}
              aria-label="Envoyer"
              className={cn(
                "flex size-8 shrink-0 items-center justify-center rounded-full transition-colors",
                chat.canSend
                  ? "bg-primary text-primary-foreground hover:bg-primary/90"
                  : "bg-muted text-muted-foreground",
              )}
            >
              <ArrowUp className="size-4" />
            </button>
          )}
        </div>
      </div>
      <p className="mt-2 text-center text-[11px] text-muted-foreground/70">
        Entrée pour envoyer · Maj+Entrée pour un saut de ligne
      </p>
    </div>
  );
});
