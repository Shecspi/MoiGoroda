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
      input
    }
  }
});
