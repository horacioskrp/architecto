import { makeAutoObservable, reaction } from "mobx";

const KEY = "architecto.sidebarOpen";

export class UiStore {
  sidebarOpen = true;

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
}
