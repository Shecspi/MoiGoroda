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
        // JS entries
        choices_css: path.resolve(entriesDir, 'choices_css.js'),
        city_all: path.resolve(entriesDir, 'city_all.js'),
        city_create: path.resolve(entriesDir, 'city_create.js'),
        city_statistics: path.resolve(entriesDir, 'city_statistics.js'),
        dashboard: path.resolve(entriesDir, 'dashboard.js'),
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
        embedded_region_map: path.resolve(entriesDir, 'embedded_region_map.js'),
        profile: path.resolve(entriesDir, 'profile.js'),
        notification: path.resolve(entriesDir, 'notification.js'),
        collection_search: path.resolve(entriesDir, 'collection_search.js'),
        collection_favorite: path.resolve(entriesDir, 'collection_favorite.js'),
        city_search: path.resolve(entriesDir, 'city_search.js'),
        preline: path.resolve(entriesDir, 'preline.js'),
        
        // CSS entries
        'css/tailwind': path.resolve(__dirname, 'css/tailwind.css'),
        'css/autoComplete': path.resolve(__dirname, 'css/autoComplete.css'),
        'css/city-card': path.resolve(__dirname, 'css/city-card.css'),
        'css/collection-cards': path.resolve(__dirname, 'css/collection-cards.css'),
        'css/pagination': path.resolve(__dirname, 'css/pagination.css'),
        'css/select-field': path.resolve(__dirname, 'css/select-field.css'),
        'css/leaflet-controls': path.resolve(__dirname, 'css/leaflet-controls.css'),
        'css/subscriptions-modal': path.resolve(__dirname, 'css/subscriptions-modal.css'),
        'css/components/checkbox': path.resolve(__dirname, 'css/components/checkbox.css'),
        'css/components/button': path.resolve(__dirname, 'css/components/button.css'),
        'css/components/badge': path.resolve(__dirname, 'css/components/badge.css'),
        'css/components/radio': path.resolve(__dirname, 'css/components/radio.css'),
        'css/components/card': path.resolve(__dirname, 'css/components/card.css'),
        'css/components/link': path.resolve(__dirname, 'css/components/link.css'),
        'css/components/typography': path.resolve(__dirname, 'css/components/typography.css'),
        'css/components/progress': path.resolve(__dirname, 'css/components/progress.css'),
        'css/toolbar': path.resolve(__dirname, 'css/toolbar.css'),
      }
    }
  }
});
