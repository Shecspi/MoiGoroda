import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(frontendRoot, '..');

export default defineConfig({
  resolve: {
    alias: {
      '@static': path.join(projectRoot, 'static'),
    },
  },
  test: {
    environment: 'happy-dom',
    include: ['ui-lib/**/*.test.js', 'js/**/*.test.js'],
  },
});
