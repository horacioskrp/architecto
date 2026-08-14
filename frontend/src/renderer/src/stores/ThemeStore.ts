import { makeAutoObservable, reaction } from "mobx";

export type Theme = "light" | "dark" | "system";

const KEY = "architecto.theme";

function systemPrefersDark(): boolean {
  return globalThis.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
}

export class ThemeStore {
  theme: Theme = "system";

  constructor() {
    const saved = localStorage.getItem(KEY) as Theme | null;
    if (saved === "light" || saved === "dark" || saved === "system") {
      this.theme = saved;
    }

    makeAutoObservable(this);

    // Applique la classe .dark et persiste à chaque changement.
    reaction(
      () => this.theme,
      (theme) => {
        localStorage.setItem(KEY, theme);
        this.apply();
      },
      { fireImmediately: true },
    );

    // Suit les changements de préférence système quand on est en mode "system".
    globalThis
      .matchMedia?.("(prefers-color-scheme: dark)")
      .addEventListener("change", () => {
        if (this.theme === "system") this.apply();
      });
  }

  get isDark(): boolean {
    return this.theme === "dark" || (this.theme === "system" && systemPrefersDark());
  }

  setTheme(theme: Theme): void {
    this.theme = theme;
  }

  /** light → dark → system → light */
  cycle(): void {
    this.theme =
      this.theme === "light" ? "dark" : this.theme === "dark" ? "system" : "light";
  }

  private apply(): void {
    document.documentElement.classList.toggle("dark", this.isDark);
  }
}
