import { makeAutoObservable, runInAction } from "mobx";

import {
  listDecisionProjects,
  listDecisions,
  type Decision,
  type DecisionProject,
} from "@/api/client";

export class DecisionsStore {
  projects: DecisionProject[] = [];
  selected = ""; // slug du projet sélectionné
  decisions: Decision[] = [];
  loadingProjects = false;
  loadingDecisions = false;
  error = "";
  loaded = false;

  constructor() {
    makeAutoObservable(this);
  }

  async loadProjects(): Promise<void> {
    this.loadingProjects = true;
    this.error = "";
    try {
      const projects = await listDecisionProjects();
      runInAction(() => {
        this.projects = projects;
        this.loaded = true;
        // sélection auto du premier projet
        if (!this.selected && projects.length > 0) {
          this.selected = projects[0].slug;
        }
      });
      if (this.selected) await this.loadDecisions(this.selected);
    } catch (e) {
      runInAction(() => {
        this.error = String(e);
      });
    } finally {
      runInAction(() => {
        this.loadingProjects = false;
      });
    }
  }

  async select(slug: string): Promise<void> {
    this.selected = slug;
    await this.loadDecisions(slug);
  }

  async loadDecisions(slug: string): Promise<void> {
    this.loadingDecisions = true;
    this.error = "";
    try {
      const decisions = await listDecisions(slug);
      runInAction(() => {
        this.decisions = decisions;
      });
    } catch (e) {
      runInAction(() => {
        this.error = String(e);
      });
    } finally {
      runInAction(() => {
        this.loadingDecisions = false;
      });
    }
  }
}
