import { makeAutoObservable, reaction } from "mobx";

const KEY = "architecto.sidebarOpen";

export class UiStore {
  sidebarOpen = true;
  knowledgeOpen = false;
  decisionsOpen = false;

  constructor() {
    const saved = localStorage.getItem(KEY);
    if (saved === "false") this.sidebarOpen = false;

    makeAutoObservable(this);

    reaction(
      () => this.sidebarOpen,
      (open) => localStorage.setItem(KEY, String(open)),
    );
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  openKnowledge(): void {
    this.knowledgeOpen = true;
  }

  closeKnowledge(): void {
    this.knowledgeOpen = false;
  }

  openDecisions(): void {
    this.decisionsOpen = true;
  }

  closeDecisions(): void {
    this.decisionsOpen = false;
  }
}
