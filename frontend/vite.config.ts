import { sentryVitePlugin } from "@sentry/vite-plugin";
import { defineConfig } from "vite";
import dns from "dns";
import react from "@vitejs/plugin-react";

dns.setDefaultResultOrder("verbatim");

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), sentryVitePlugin({
    org: "dchavro",
    project: "pingcycle-frontend"
  })],

  server: {
    host: "127.0.0.1",
    port: 3000,
  },

  build: {
    sourcemap: true
  }
});