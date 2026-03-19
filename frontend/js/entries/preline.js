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

  // TODO(2026-04-02): Удалить временный анонс новой функции генератора изображения региона.
  // BEGIN TEMP_REGION_SHARE_FEATURE_ANNOUNCEMENT
  // Авто-открытие модалки анонса генератора изображения региона (если присутствует в DOM)
  const regionShareFeatureModal = document.getElementById('modal_region_share_feature_announcement');
  if (regionShareFeatureModal) {
    const forceShowRegionShareFeatureAnnouncement = new URLSearchParams(window.location.search).get('show_feature_announcement') === '1';
    const regionShareFeatureAnnouncementStorageKey = 'region_share_feature_announcement_seen_v1';
    const isRegionShareFeatureAnnouncementSeen = localStorage.getItem(
      regionShareFeatureAnnouncementStorageKey,
    ) === '1';

    if (forceShowRegionShareFeatureAnnouncement || !isRegionShareFeatureAnnouncementSeen) {
      setTimeout(() => {
        HSOverlay.open('#modal_region_share_feature_announcement');
      }, 100);

      localStorage.setItem(regionShareFeatureAnnouncementStorageKey, '1');
    }
  }
  // END TEMP_REGION_SHARE_FEATURE_ANNOUNCEMENT

  // Сохранение выбора «Больше не показывать»
  const dismissBtn = document.getElementById('premium-promo-dismiss');
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      localStorage.setItem('premium_promo_dismissed', 'true');
    });
  }
});

