// Correspondance nom d'outil backend -> libellé lisible affiché pendant le flux.
const LABELS: Record<string, string> = {
  search_knowledge_base: "Consulte la base de connaissances",
  generate_diagram: "Génère un diagramme",
  generate_adr: "Rédige un ADR",
  generate_architecture: "Conçoit l'architecture",
  design_database: "Conçoit la base de données",
  security_checklist: "Vérifie la sécurité (OWASP)",
  analyze_dependencies: "Analyse les dépendances",
  save_decision: "Enregistre une décision",
  recall_decisions: "Consulte les décisions",
};

export function toolLabel(name: string): string {
  return LABELS[name] ?? `Outil : ${name}`;
}
