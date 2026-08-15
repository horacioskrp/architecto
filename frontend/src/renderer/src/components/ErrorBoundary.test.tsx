import "@testing-library/jest-dom/vitest";

import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import { ErrorBoundary } from "@/components/ErrorBoundary";

function Boom(): never {
  throw new Error("boom test");
}

/** Silence l'erreur console émise par React lors de la capture (attendue). */
function silenceConsoleError() {
  return vi.spyOn(console, "error").mockImplementation(() => {});
}

describe("ErrorBoundary", () => {
  it("rend les enfants quand tout va bien", () => {
    render(
      <ErrorBoundary>
        <p>contenu ok</p>
      </ErrorBoundary>,
    );
    expect(screen.getByText("contenu ok")).toBeInTheDocument();
  });

  it("affiche le repli plein écran quand un enfant jette", () => {
    const spy = silenceConsoleError();
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByText(/erreur inattendue/i)).toBeInTheDocument();
    expect(screen.getByText("boom test")).toBeInTheDocument();
    spy.mockRestore();
  });

  it("utilise un repli personnalisé (fonction) avec l'erreur", () => {
    const spy = silenceConsoleError();
    render(
      <ErrorBoundary fallback={(err) => <span>repli : {err.message}</span>}>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByText("repli : boom test")).toBeInTheDocument();
    spy.mockRestore();
  });
});
