import { Component, type ReactNode } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { useRouteError } from "react-router-dom";

type Fallback = ReactNode | ((error: Error, reset: () => void) => ReactNode);

interface Props {
  children: ReactNode;
  /** Repli personnalisé. Par défaut : écran plein d'erreur. */
  fallback?: Fallback;
  onError?: (error: Error) => void;
}

interface State {
  error: Error | null;
}

/**
 * Capture les erreurs de rendu React et affiche un repli au lieu d'un écran
 * blanc. Les *boundaries* React sont forcément des composants classe.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error): void {
    this.props.onError?.(error);
    // Trace pour le débogage (visible dans la console du renderer).
    console.error("ErrorBoundary a intercepté une erreur :", error);
  }

  reset = (): void => this.setState({ error: null });

  render(): ReactNode {
    const { error } = this.state;
    if (!error) return this.props.children;

    const { fallback } = this.props;
    if (typeof fallback === "function") return fallback(error, this.reset);
    if (fallback !== undefined) return fallback;
    return <FullScreenFallback error={error} reset={this.reset} />;
  }
}

/**
 * `errorElement` pour React Router : le *data router* intercepte les erreurs de
 * route avant tout boundary React placé au-dessus de `RouterProvider`. On lit
 * l'erreur via `useRouteError` et on affiche le même repli plein écran.
 */
export function RouteErrorFallback() {
  const routeError = useRouteError();
  const error =
    routeError instanceof Error ? routeError : new Error(String(routeError));
  return <FullScreenFallback error={error} reset={() => window.location.reload()} />;
}

function FullScreenFallback({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-4 bg-background p-6 text-center">
      <AlertTriangle className="size-10 text-destructive" />
      <div>
        <h1 className="text-lg font-semibold">Une erreur inattendue est survenue</h1>
        <p className="mt-1 max-w-md text-sm text-muted-foreground">
          L'interface a rencontré un problème. Tes conversations restent
          enregistrées.
        </p>
      </div>
      <pre className="max-w-lg overflow-x-auto rounded-lg border border-border bg-muted px-3 py-2 text-left text-xs text-muted-foreground">
        {error.message}
      </pre>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={reset}
          className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          <RotateCcw className="size-4" />
          Réessayer
        </button>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="rounded-lg border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
        >
          Recharger l'app
        </button>
      </div>
    </div>
  );
}

/** Repli compact, pour isoler une petite zone (ex. un message qui plante). */
export function InlineErrorFallback({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex items-center justify-between gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
      <span className="flex items-center gap-2">
        <AlertTriangle className="size-4 shrink-0" />
        Ce contenu n'a pas pu s'afficher.
      </span>
      <button
        type="button"
        onClick={reset}
        className="shrink-0 rounded p-1 transition hover:bg-destructive/10"
        aria-label="Réessayer"
      >
        <RotateCcw className="size-4" />
      </button>
    </div>
  );
}
