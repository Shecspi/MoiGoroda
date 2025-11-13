import 'preline';

document.addEventListener('DOMContentLoaded', () => {
  // Инициализация Preline UI
  // autoInit() автоматически инициализирует все компоненты Preline, включая tooltips
  if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
    window.HSStaticMethods.autoInit();
  }
});

