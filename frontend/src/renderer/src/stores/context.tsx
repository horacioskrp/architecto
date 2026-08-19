import { createContext, useContext, type ReactNode } from "react";

import { RootStore } from "@/stores/RootStore";

const rootStore = new RootStore();
// Charge l'historique persisté (durable/IPC) après construction ; MobX met à
// jour l'UI quand les conversations arrivent.
void rootStore.chat.hydrate();
const StoreContext = createContext<RootStore>(rootStore);

export function StoreProvider({ children }: { children: ReactNode }) {
  return (
    <StoreContext.Provider value={rootStore}>{children}</StoreContext.Provider>
  );
}

export function useStores(): RootStore {
  return useContext(StoreContext);
}
