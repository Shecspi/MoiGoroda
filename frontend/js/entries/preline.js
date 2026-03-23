/**
 * Preline UI: динамический импорт, autoInit для селектов и т.д.
 * HSDatepicker не используется — даты полей посещения на кастомном visit_date_picker.js.
 */
async function bootstrap() {
  await import('preline');
  const { HSOverlay } = await import('preline');

  function initUi() {
    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
      window.HSStaticMethods.autoInit();
    }

    const promoModal = document.getElementById('premium-promo-modal');
    if (promoModal && !localStorage.getItem('premium_promo_dismissed')) {
      setTimeout(() => {
        HSOverlay.open('#premium-promo-modal');
      }, 100);
    }

    const regionShareFeatureModal = document.getElementById('modal_region_share_feature_announcement');
    if (regionShareFeatureModal) {
      const forceShowRegionShareFeatureAnnouncement =
        new URLSearchParams(window.location.search).get('show_feature_announcement') === '1';
      const regionShareFeatureAnnouncementStorageKey = 'region_share_feature_announcement_seen_v1';
      const isRegionShareFeatureAnnouncementSeen =
        localStorage.getItem(regionShareFeatureAnnouncementStorageKey) === '1';

      if (forceShowRegionShareFeatureAnnouncement || !isRegionShareFeatureAnnouncementSeen) {
        setTimeout(() => {
          HSOverlay.open('#modal_region_share_feature_announcement');
        }, 100);

        localStorage.setItem(regionShareFeatureAnnouncementStorageKey, '1');
      }
    }

    const dismissBtn = document.getElementById('premium-promo-dismiss');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', () => {
        localStorage.setItem('premium_promo_dismissed', 'true');
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUi);
  } else {
    initUi();
  }
}

bootstrap();
