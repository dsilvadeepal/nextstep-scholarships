import { defineConfig } from "@playwright/test";

// Explicit opt-in: these checks use the real local corpus and two paid chat calls.
export default defineConfig({
  testDir: "./live-e2e",
  timeout: 60_000,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:8014" },
  projects: [
    { name: "phone", use: { viewport: { width: 390, height: 844 } } },
    { name: "desktop", use: { viewport: { width: 1440, height: 1000 } } },
  ],
});
