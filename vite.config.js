import { defineConfig } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';
import svgLoader from 'vite-svg-loader';

export default defineConfig({
  base: "/static/",
  plugins: [
    vue(),
    svgLoader({
      defaultImport: 'raw' // or 'raw'
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    origin: 'http://localhost:5173',
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
        mount_vue: resolve("./desparchado/frontend/scripts/mount-vue.ts"),
        main_styles: resolve("./desparchado/frontend/styles/index.scss"),
        base: resolve("./desparchado/frontend/scripts/base.ts"),
        event_detail: resolve("./desparchado/frontend/scripts/event-detail.ts"),
        events: resolve("./desparchado/frontend/scripts/events.ts"),
        generic: resolve("./desparchado/frontend/scripts/generic.ts"),
        home: resolve("./desparchado/frontend/scripts/home.ts"),
        playground: resolve("./desparchado/static/ts/playground.ts"),
        old_main: resolve("./desparchado/static/ts/old_main.ts"),
        posts_pagination_initializer: resolve("./desparchado/static/ts/posts_pagination_initializer.ts"),
        dashboard: resolve("./desparchado/static/js/dashboard.js")
      }
    }
  },
  resolve: {
    alias: {
      "@presentational_components": resolve("./desparchado/frontend/components/presentational"),
      "@styles": resolve("./desparchado/frontend/styles"),
      "@fonts": resolve("./desparchado/frontend/assets/fonts"),
      "@assets": resolve("./desparchado/frontend/assets"),
    }
  }
})
