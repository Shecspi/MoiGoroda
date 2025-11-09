import 'preline';

document.addEventListener('DOMContentLoaded', () => {
  if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
    window.HSStaticMethods.autoInit();
  }
});

