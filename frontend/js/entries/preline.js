import 'preline';
import { HSOverlay } from 'preline';

document.addEventListener('DOMContentLoaded', () => {
  // Инициализация Preline UI
  // autoInit() автоматически инициализирует все компоненты Preline, включая tooltips
  if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
    window.HSStaticMethods.autoInit();
  }

  // Открытие модалки премиум-промо при загрузке (если есть на странице и пользователь ещё не скрыл её)
  const promoModal = document.getElementById('premium-promo-modal');
  if (promoModal && !localStorage.getItem('premium_promo_dismissed')) {
    setTimeout(() => {
      HSOverlay.open('#premium-promo-modal');
    }, 100);
  }

  // Сохранение выбора «Больше не показывать»
  const dismissBtn = document.getElementById('premium-promo-dismiss');
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      localStorage.setItem('premium_promo_dismissed', 'true');
    });
  }
});

