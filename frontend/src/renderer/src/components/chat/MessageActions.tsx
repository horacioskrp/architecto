import { useState } from "react";
import { Check, Copy, RotateCcw } from "lucide-react";

interface Props {
  content: string;
  canRegenerate: boolean;
  onRegenerate: () => void;
}

/**
 * Barre d'actions d'un message assistant (copier, régénérer).
 * Révélée au survol de la bulle parente (classe `group/msg`).
 */
export function MessageActions({ content, canRegenerate, onRegenerate }: Props) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // presse-papier indisponible : on ignore silencieusement
    }
  };

  return (
    <div className="mt-1 flex items-center gap-1 text-muted-foreground opacity-0 transition-opacity group-hover/msg:opacity-100">
      <button
        type="button"
        onClick={copy}
        className="flex items-center gap-1 rounded-md px-2 py-1 text-xs transition-colors hover:bg-accent hover:text-foreground"
        aria-label="Copier le message"
      >
        {copied ? (
          <>
            <Check className="size-3.5" /> Copié
          </>
        ) : (
          <>
            <Copy className="size-3.5" /> Copier
          </>
        )}
      </button>

      {canRegenerate && (
        <button
          type="button"
          onClick={onRegenerate}
          className="flex items-center gap-1 rounded-md px-2 py-1 text-xs transition-colors hover:bg-accent hover:text-foreground"
          aria-label="Régénérer la réponse"
        >
          <RotateCcw className="size-3.5" /> Régénérer
        </button>
      )}
    </div>
  );
}
