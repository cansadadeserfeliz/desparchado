import { defineConfig } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  base: "/static/",
  plugins: [vue()],
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
        dashboard: resolve("./desparchado/static/js/dashboard.js"),
        mount_vue: resolve("./desparchado/frontend/scripts/mount-vue.ts"),
        main_styles: resolve("./desparchado/frontend/styles/index.scss")
      }
    }
  },
  resolve: {
    alias: {
      "@presentational_components": resolve("./desparchado/frontend/components/presentational"),
      "@styles": resolve("./desparchado/frontend/styles"),
    }
  }
})
