import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: "/static/",
  server: {
    host: '0.0.0.0',
    port: 5173,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  build: {
    manifest: "manifest.json",
    outDir: resolve("./desparchado/static/dist"),
    rollupOptions: {
      input: {
        old_main: resolve("./desparchado/static/ts/old_main.ts"),
        playground: resolve("./desparchado/static/ts/playground.ts"),
        dashboard: resolve("./desparchado/static/js/dashboard.js")
      }
    }
  }
})
