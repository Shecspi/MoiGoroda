// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

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
