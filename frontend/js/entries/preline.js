import 'preline';
import { HSOverlay } from 'preline';

document.addEventListener('DOMContentLoaded', () => {
  // Инициализация Preline UI
  // autoInit() автоматически инициализирует все компоненты Preline, включая tooltips
  if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
    window.HSStaticMethods.autoInit();
  }

  // Открытие модалки премиум-промо при загрузке (если есть на странице)
  const promoModal = document.getElementById('premium-promo-modal');
  if (promoModal) {
    setTimeout(() => {
      HSOverlay.open('#premium-promo-modal');
    }, 100);
  }
});

