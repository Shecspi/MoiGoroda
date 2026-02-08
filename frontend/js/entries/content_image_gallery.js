/**
 * Галерея изображений для контента статей и новостей.
 * При клике на изображение открывается модальное окно с каруселью для просмотра в полном размере.
 *
 * Требует Preline (HSOverlay, HSCarousel).
 */
import 'preline';

const MODAL_ID = '#image-gallery-modal';
const CAROUSEL_ID = '#image-gallery-carousel';
const CAROUSEL_BODY_SELECTOR = `${CAROUSEL_ID} .hs-carousel-body`;

function initContentImageGallery() {
  // Убеждаемся, что модалка в DOM (она подключается из base.html)
  const modal = document.querySelector(MODAL_ID);
  if (!modal) return;

  // Preline мог загрузиться после DOMContentLoaded — инициализируем overlay
  if (window.HSStaticMethods?.autoInit) {
    window.HSStaticMethods.autoInit();
  }
  const containers = document.querySelectorAll('.content-with-image-gallery');
  if (containers.length === 0) return;

  containers.forEach((container) => {
    const images = container.querySelectorAll('img[src]');
    if (images.length === 0) return;

    images.forEach((img, index) => {
      img.addEventListener('click', (e) => {
        e.preventDefault();
        openGallery(container, index);
      });
    });
  });
}

function openGallery(container, startIndex) {
  const HSCarousel = window.HSCarousel;

  const images = Array.from(container.querySelectorAll('img[src]'));
  if (images.length === 0) return;

  const srcs = images.map((img) => img.src || img.getAttribute('src')).filter(Boolean);
  if (srcs.length === 0) return;

  const carouselBody = document.querySelector(CAROUSEL_BODY_SELECTOR);
  const carouselEl = document.querySelector(CAROUSEL_ID);
  if (!carouselBody || !carouselEl) return;

  // Destroy previous carousel instance if exists
  if (HSCarousel) {
    try {
      const instance = HSCarousel.getInstance(carouselEl);
      if (instance?.element?.destroy) {
        instance.element.destroy();
      }
    } catch (_e) {
      // No existing instance
    }
  }

  // Build slides HTML
  const slidesHtml = srcs
    .map(
      (src) => `
    <div class="hs-carousel-slide flex-shrink-0 w-full">
      <div class="flex justify-center items-center bg-gray-100 dark:bg-neutral-800 p-4 min-h-[300px] max-h-[80vh]">
        <img src="${escapeHtml(src)}" alt="" class="max-w-full max-h-[75vh] w-auto h-auto object-contain rounded-lg">
      </div>
    </div>
  `
    )
    .join('');

  carouselBody.innerHTML = slidesHtml;

  // Update carousel config with currentIndex
  const config = {
    loadingClasses: 'opacity-0',
    dotsItemClasses:
      'hs-carousel-active:bg-blue-700 size-3 border border-gray-400 rounded-full cursor-pointer dark:border-neutral-600 dark:hs-carousel-active:bg-blue-500',
    isAutoPlay: false,
    isInfiniteLoop: true,
    currentIndex: Math.min(startIndex, srcs.length - 1),
  };
  carouselEl.setAttribute('data-hs-carousel', JSON.stringify(config));

  // Initialize carousel (HSCarousel is from Preline)
  if (HSCarousel) {
    try {
      new HSCarousel(carouselEl);
    } catch (_e) {
      // Fallback to autoInit
      if (window.HSStaticMethods?.autoInit) {
        window.HSStaticMethods.autoInit(['carousel']);
      }
    }
  }

  // Открываем модалку: сначала autoInit, затем клик по триггеру (надёжный способ)
  const overlayEl = document.querySelector(MODAL_ID);
  if (!overlayEl) return;

  if (window.HSOverlay) {
    try {
      window.HSOverlay.autoInit();
      window.HSOverlay.open(overlayEl);
    } catch (_e) {
      // Fallback: клик по скрытой кнопке-триггеру
      const trigger = document.getElementById('image-gallery-modal-trigger');
      if (trigger) trigger.click();
    }
  } else {
    const trigger = document.getElementById('image-gallery-modal-trigger');
    if (trigger) trigger.click();
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// Модульные скрипты загружаются с defer — DOMContentLoaded может уже сработать
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initContentImageGallery);
} else {
  initContentImageGallery();
}
