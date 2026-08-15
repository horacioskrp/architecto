import "@testing-library/jest-dom/vitest";

import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// Démonte les composants rendus entre chaque test (évite les fuites de DOM).
afterEach(() => {
  cleanup();
});
