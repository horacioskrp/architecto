import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center gap-4 py-20 text-center">
      <h1 className="text-2xl font-semibold">404</h1>
      <p className="text-sm text-muted-foreground">Page introuvable.</p>
      <Button asChild variant="outline">
        <Link to="/">Retour à l'accueil</Link>
      </Button>
    </div>
  );
}
