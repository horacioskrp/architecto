import { useEffect, useRef, useState } from "react";
import { observer } from "mobx-react-lite";
import { FileText, Loader2, Trash2, Upload } from "lucide-react";

import { Modal } from "@/components/ui/modal";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

const ACCEPT = ".md,.txt,.pdf";

export const KnowledgeModal = observer(function KnowledgeModal() {
  const { ui, knowledge } = useStores();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (ui.knowledgeOpen) void knowledge.load();
  }, [ui.knowledgeOpen, knowledge]);

  const onFiles = (list: FileList | null) => {
    if (!list || list.length === 0) return;
    void knowledge.ingest([...list]);
  };

  const result = knowledge.lastResult;

  return (
    <Modal
      open={ui.knowledgeOpen}
      onClose={() => ui.closeKnowledge()}
      title="Base de connaissances"
      description="Ancre les réponses de l'agent sur tes propres documents (RAG)."
    >
      <div className="flex flex-col gap-4">
        {/* Zone de dépôt */}
        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            onFiles(e.dataTransfer.files);
          }}
          className={cn(
            "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-4 py-8 text-center transition-colors",
            dragging
              ? "border-clay bg-clay/5"
              : "border-border hover:border-muted-foreground/40 hover:bg-accent/40",
          )}
        >
          {knowledge.busy ? (
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
          ) : (
            <Upload className="size-6 text-muted-foreground" />
          )}
          <div className="text-sm">
            <span className="font-medium">Clique ou dépose des fichiers</span>
            <p className="text-xs text-muted-foreground">
              .md, .txt, .pdf — réingérer un fichier met à jour son contenu
            </p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            multiple
            className="hidden"
            onChange={(e) => {
              onFiles(e.target.files);
              e.target.value = "";
            }}
          />
        </div>

        {knowledge.error && (
          <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {knowledge.error}
          </p>
        )}

        {result && (
          <p className="rounded-lg border border-border bg-muted/50 px-3 py-2 text-xs text-muted-foreground">
            {result.processed} traité(s) · {result.skipped_unchanged} inchangé(s) ·{" "}
            {result.chunks} fragment(s) créé(s)
            {result.rejected.length > 0 && (
              <>
                {" "}
                · rejeté(s) : {result.rejected.join(", ")}
              </>
            )}
          </p>
        )}

        {/* Liste des sources */}
        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between px-1 text-xs text-muted-foreground">
            <span>
              {knowledge.sources.length} document(s) · {knowledge.totalChunks} fragment(s)
            </span>
            {knowledge.loading && <Loader2 className="size-3.5 animate-spin" />}
          </div>

          {knowledge.loaded && knowledge.sources.length === 0 && !knowledge.loading ? (
            <p className="px-1 py-6 text-center text-sm text-muted-foreground">
              Aucun document pour l'instant.
            </p>
          ) : (
            <ul className="flex flex-col gap-1">
              {knowledge.sources.map((s) => (
                <li
                  key={s.source}
                  className="group flex items-center gap-2 rounded-lg border border-border px-3 py-2"
                >
                  <FileText className="size-4 shrink-0 text-muted-foreground" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium" title={s.source}>
                      {s.title}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {s.source} · {s.chunk_count} fragment(s)
                    </p>
                  </div>
                  <button
                    type="button"
                    aria-label={`Supprimer ${s.title}`}
                    disabled={knowledge.busy}
                    onClick={() => void knowledge.remove(s.source)}
                    className="shrink-0 rounded p-1 text-muted-foreground transition hover:text-destructive disabled:opacity-40"
                  >
                    <Trash2 className="size-4" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Modal>
  );
});
