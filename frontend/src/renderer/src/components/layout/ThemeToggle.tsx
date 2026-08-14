import { observer } from "mobx-react-lite";
import { Monitor, Moon, Sun } from "lucide-react";

import { useStores } from "@/stores/context";

const LABELS = { light: "Clair", dark: "Sombre", system: "Système" } as const;

export const ThemeToggle = observer(function ThemeToggle() {
  const { theme } = useStores();
  const Icon = theme.theme === "light" ? Sun : theme.theme === "dark" ? Moon : Monitor;

  return (
    <button
      type="button"
      onClick={() => theme.cycle()}
      className="flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
      title={`Thème : ${LABELS[theme.theme]} (cliquer pour changer)`}
      aria-label={`Thème : ${LABELS[theme.theme]}`}
    >
      <Icon className="size-4" />
      <span>{LABELS[theme.theme]}</span>
    </button>
  );
});
