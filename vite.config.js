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
        main: resolve("./desparchado/static/ts/main.ts"),
        dashboard: resolve("./desparchado/static/js/dashboard.js")
      }
    }
  }
})
