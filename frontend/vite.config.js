import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: __dirname,
  base: '/',
  server: {
    origin: 'http://localhost:5173',
    port: 5173,
    strictPort: true
  },
  build: {
    outDir: '../static/js',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        map_city: path.resolve(__dirname, 'js/entries/map_city.js')
      }
    }
  }
});
