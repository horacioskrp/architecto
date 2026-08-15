import { useEffect, useState } from "react";
import { observer } from "mobx-react-lite";
import { Check, Copy, Loader2 } from "lucide-react";

import type { Decision } from "@/api/client";
import { Modal } from "@/components/ui/modal";
import { decisionToAdr } from "@/lib/adr";
import { cn } from "@/lib/utils";
import { useStores } from "@/stores/context";

export const DecisionsModal = observer(function DecisionsModal() {
  const { ui, decisions } = useStores();

  useEffect(() => {
    if (ui.decisionsOpen) void decisions.loadProjects();
  }, [ui.decisionsOpen, decisions]);

  return (
    <Modal
      open={ui.decisionsOpen}
      onClose={() => ui.closeDecisions()}
      title="Décisions d'architecture"
      description="Les ADR mémorisés par l'agent, regroupés par projet."
    >
      <div className="flex flex-col gap-4">
        {decisions.error && (
          <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {decisions.error}
          </p>
        )}

        {/* Sélecteur de projet */}
        {decisions.projects.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {decisions.projects.map((p) => (
              <button
                key={p.slug}
                type="button"
                onClick={() => void decisions.select(p.slug)}
                className={cn(
                  "rounded-full border px-3 py-1 text-xs transition-colors",
                  p.slug === decisions.selected
                    ? "border-transparent bg-primary text-primary-foreground"
                    : "border-border text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
              >
                {p.name}
                <span className="ml-1 opacity-70">({p.decision_count})</span>
              </button>
            ))}
          </div>
        )}

        {decisions.loadingProjects ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <Loader2 className="size-5 animate-spin" />
          </div>
        ) : decisions.loaded && decisions.projects.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Aucune décision mémorisée pour l'instant. L'agent en enregistre au fil
            des conversations (associe un projet dans le composer).
          </p>
        ) : (
          <div className="flex flex-col gap-3">
            {decisions.loadingDecisions ? (
              <div className="flex items-center justify-center py-6 text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
              </div>
            ) : (
              decisions.decisions.map((d) => <DecisionCard key={d.id} decision={d} />)
            )}
          </div>
        )}
      </div>
    </Modal>
  );
});

function DecisionCard({ decision }: { decision: Decision }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(decisionToAdr(decision));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard indisponible */
    }
  };

  return (
    <article className="rounded-xl border border-border p-4">
      <header className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-medium">{decision.title}</h3>
          <span className="mt-1 inline-block rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
            {decision.status}
          </span>
        </div>
        <button
          type="button"
          onClick={() => void copy()}
          className="flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          title="Copier en ADR Markdown"
        >
          {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
          {copied ? "Copié" : "Copier en ADR"}
        </button>
      </header>

      <dl className="mt-3 space-y-2 text-sm">
        <Field label="Contexte" value={decision.context} />
        <Field label="Décision" value={decision.decision} />
        <Field label="Conséquences" value={decision.consequences} />
      </dl>
    </article>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap text-foreground">{value}</dd>
    </div>
  );
}
