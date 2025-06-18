import { defineConfig } from 'vite';
import path from 'path';
import fs from 'fs';

// Получаем все entry-файлы из js/entries
const entriesDir = path.resolve(__dirname, 'js/entries');
const entryFiles = fs.readdirSync(entriesDir).filter(file => file.endsWith('.js'));

const input = {};
entryFiles.forEach(file => {
  const name = path.parse(file).name;
  input[name] = path.resolve(entriesDir, file);
});

export default defineConfig({
  root: __dirname,
  base: '/static/js/',  // это путь, по которому Django будет искать скрипты
  server: {
    origin: 'http://localhost:5173',
    port: 5173,
    strictPort: true
  },
  build: {
    outDir: '../static/js', // папка, куда попадёт сборка
    emptyOutDir: true,
    manifest: true, // нужен для Django
    rollupOptions: {
      input: {
        city_all: path.resolve(entriesDir, 'city_all.js'),
        city_create: path.resolve(entriesDir, 'city_create.js'),
        city_statistics: path.resolve(entriesDir, 'city_statistics.js'),
        dashboard: path.resolve(entriesDir, 'dashboard.js'),
        enable_tooltips: path.resolve(entriesDir, 'enable_tooltips.js'),
        filter_city: path.resolve(entriesDir, 'filter_city.js'),
        filter_region: path.resolve(entriesDir, 'filter_region.js'),
        leaflet_css: path.resolve(entriesDir, 'leaflet_css.js'),
        map_city: path.resolve(entriesDir, 'map_city.js'),
        map_city_selected: path.resolve(entriesDir, 'map_city_selected.js'),
        map_collection: path.resolve(entriesDir, 'map_collection.js'),
        map_country: path.resolve(entriesDir, 'map_country.js'),
        map_place: path.resolve(entriesDir, 'map_place.js'),
        map_region: path.resolve(entriesDir, 'map_region.js'),
        map_region_selected: path.resolve(entriesDir, 'map_region_selected.js'),
        map_share: path.resolve(entriesDir, 'map_share.js'),
        region_all: path.resolve(entriesDir, 'region_all.js'),
        share_modal: path.resolve(entriesDir, 'share_modal.js'),
        sidebar: path.resolve(entriesDir, 'sidebar.js'),
        subscribe_api: path.resolve(entriesDir, 'subscribe_api.js'),
        signup: path.resolve(entriesDir, 'signup.js'),
        travelpayouts_verify: path.resolve(entriesDir, 'travelpayouts_verify.js'),
      }
    }
  }
});
