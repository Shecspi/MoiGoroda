/**
 * Открывает модальное окно с информацией о премиум-подписке при загрузке страницы.
 * Вызывается только для авторизованных пользователей без активной подписки.
 */
import { HSOverlay } from 'preline';

document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('premium-promo-modal');
  if (!modal) return;

  setTimeout(function () {
    HSOverlay.open('#premium-promo-modal');
  }, 100);
});
