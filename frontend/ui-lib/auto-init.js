import { registerDefaultComponents, initAll, destroyAll } from './index';

registerDefaultComponents();

function bootstrap() {
  initAll(document);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}

window.MGUi = {
  initAll,
  destroyAll,
};
