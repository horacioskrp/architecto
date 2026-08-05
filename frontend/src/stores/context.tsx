import { createContext, useContext, type ReactNode } from "react";

import { RootStore } from "@/stores/RootStore";

const rootStore = new RootStore();
const StoreContext = createContext<RootStore>(rootStore);

export function StoreProvider({ children }: { children: ReactNode }) {
  return (
    <StoreContext.Provider value={rootStore}>{children}</StoreContext.Provider>
  );
}

export function useStores(): RootStore {
  return useContext(StoreContext);
}
