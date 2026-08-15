import { makeAutoObservable, runInAction } from "mobx";

import {
  deleteSource,
  ingestFiles,
  listSources,
  type IngestResult,
  type KnowledgeSource,
} from "@/api/client";

export class KnowledgeStore {
  sources: KnowledgeSource[] = [];
  loading = false;
  busy = false; // ingestion ou suppression en cours
  error = "";
  lastResult: IngestResult | null = null;
  loaded = false;

  constructor() {
    makeAutoObservable(this);
  }

  get totalChunks(): number {
    return this.sources.reduce((sum, s) => sum + s.chunk_count, 0);
  }

  async load(): Promise<void> {
    this.loading = true;
    this.error = "";
    try {
      const sources = await listSources();
      runInAction(() => {
        this.sources = sources;
        this.loaded = true;
      });
    } catch (e) {
      runInAction(() => {
        this.error = String(e);
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
  }

  async ingest(files: File[]): Promise<void> {
    if (files.length === 0 || this.busy) return;
    this.busy = true;
    this.error = "";
    this.lastResult = null;
    try {
      const result = await ingestFiles(files);
      runInAction(() => {
        this.lastResult = result;
      });
      await this.load();
    } catch (e) {
      runInAction(() => {
        this.error = String(e);
      });
    } finally {
      runInAction(() => {
        this.busy = false;
      });
    }
  }

  async remove(source: string): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.error = "";
    try {
      await deleteSource(source);
      runInAction(() => {
        this.sources = this.sources.filter((s) => s.source !== source);
      });
    } catch (e) {
      runInAction(() => {
        this.error = String(e);
      });
    } finally {
      runInAction(() => {
        this.busy = false;
      });
    }
  }
}
