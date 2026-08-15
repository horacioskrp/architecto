import type { Decision } from "@/api/client";

/** Formate une décision en ADR Markdown, prêt à copier/exporter. */
export function decisionToAdr(d: Decision): string {
  return [
    `# ${d.title}`,
    "",
    `**Statut :** ${d.status}`,
    "",
    "## Contexte",
    "",
    d.context,
    "",
    "## Décision",
    "",
    d.decision,
    "",
    "## Conséquences",
    "",
    d.consequences,
    "",
  ].join("\n");
}
