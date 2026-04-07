import GLightbox from 'glightbox';
import 'glightbox/dist/css/glightbox.min.css';
import '../../css/city_glightbox.css';
import Swiper from 'swiper';
import { Navigation, Pagination, Manipulation, Thumbs, FreeMode } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import 'swiper/css/free-mode';
import 'swiper/css/thumbs';
import { getCookie } from '../components/get_cookie';
import { openConfirmModal } from '../components/confirm_modal';

let lightboxInstance = null;

/** Тот же path, что у стрелок Swiper на странице города (image_section.html). */
const CITY_GLIGHTBOX_ARROW_PATH =
  'M566.6 342.6C579.1 330.1 579.1 309.8 566.6 297.3L406.6 137.3C394.1 124.8 373.8 124.8 361.3 137.3C348.8 149.8 348.8 170.1 361.3 182.6L466.7 288L96 288C78.3 288 64 302.3 64 320C64 337.7 78.3 352 96 352L466.7 352L361.3 457.4C348.8 469.9 348.8 490.2 361.3 502.7C373.8 515.2 394.1 515.2 406.6 502.7L566.6 342.7z';

const cityGlightboxArrowSvgs = {
  next: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="currentColor" aria-hidden="true"><path d="${CITY_GLIGHTBOX_ARROW_PATH}"/></svg>`,
  prev: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="currentColor" aria-hidden="true"><g transform="translate(640 0) scale(-1 1)"><path d="${CITY_GLIGHTBOX_ARROW_PATH}"/></g></svg>`,
};

function initCityGallery() {
  const sectionRoot = document.getElementById('section-city_image');
  if (!(sectionRoot instanceof HTMLElement)) return;
  const galleryLinks = sectionRoot.querySelectorAll('.city-glightbox');
  if (galleryLinks.length === 0) return;

  if (lightboxInstance) {
    lightboxInstance.destroy();
  }

  lightboxInstance = GLightbox({
    selector: '#section-city_image .city-glightbox',
    touchNavigation: true,
    loop: true,
    autoplayVideos: false,
    svg: {
      next: cityGlightboxArrowSvgs.next,
      prev: cityGlightboxArrowSvgs.prev,
    },
    onOpen: () => {
      document.getElementById('glightbox-body')?.classList.add('glightbox-city-photo');
    },
    onClose: () => {
      document.getElementById('glightbox-body')?.classList.remove('glightbox-city-photo');
    },
  });
}

function showError(message) {
  const errorNode = document.getElementById('city-photo-error');
  if (!errorNode) return;
  errorNode.textContent = message;
  errorNode.classList.remove('hidden', 'text-amber-700', 'dark:text-amber-400');
  errorNode.classList.add('text-red-600');
}

function showCityPhotoUploadNotice(message) {
  const errorNode = document.getElementById('city-photo-error');
  if (!errorNode) return;
  errorNode.textContent = message;
  errorNode.classList.remove('hidden', 'text-red-600');
  errorNode.classList.add('text-amber-700', 'dark:text-amber-400');
}

function hideCityPhotoUploadMessage() {
  const errorNode = document.getElementById('city-photo-error');
  if (!errorNode) return;
  errorNode.textContent = '';
  errorNode.classList.add('hidden');
  errorNode.classList.remove('text-amber-700', 'dark:text-amber-400');
  errorNode.classList.add('text-red-600');
}

/** Панель миниатюр скрыта шаблоном, пока нет ни одного реального изображения (нет user photos и нет city.image). */
function isCityPhotoThumbsPanelHidden(panel) {
  if (!(panel instanceof HTMLElement)) return true;
  return panel.classList.contains('hidden');
}

function showCityPhotoThumbsPanel(panel) {
  if (!(panel instanceof HTMLElement)) return;
  panel.classList.remove('hidden');
  panel.setAttribute('aria-hidden', 'false');
}

function hideCityPhotoThumbsPanel(panel) {
  if (!(panel instanceof HTMLElement)) return;
  panel.classList.add('hidden');
  panel.setAttribute('aria-hidden', 'true');
}

function hideCityPhotoNoImageMessages() {
  const el = document.getElementById('city-photo-no-image-messages');
  if (el instanceof HTMLElement) {
    el.classList.add('hidden');
  }
}

function showCityPhotoNoImageMessages() {
  const el = document.getElementById('city-photo-no-image-messages');
  if (el instanceof HTMLElement) {
    el.classList.remove('hidden');
  }
}

const CITY_PHOTO_STAGE_CLASS = 'city-photo-stage';
const CITY_PHOTO_STAGE_PLACEHOLDER_CLASS = 'city-photo-stage city-photo-stage--placeholder';

const CITY_PHOTO_THUMB_SLIDE_BASE_CLASS =
  'swiper-slide block p-0 appearance-none relative !w-20 !h-14 rounded-md overflow-hidden border border-layer-line bg-layer cursor-pointer opacity-50 transition-opacity duration-200 ease-out [&.swiper-slide-thumb-active]:opacity-100';

/** Лимит пользовательских фото на город (совпадает с API). */
const MAX_CITY_USER_PHOTOS = 5;

function countCityUserPhotosInCarousel(citySwiper) {
  if (!citySwiper?.el) return 0;
  return citySwiper.el.querySelectorAll('.swiper-slide[data-photo-id]:not([data-photo-id=""])').length;
}

function truncateCityPhotoFileName(name, maxLen = 40) {
  const s = String(name || '');
  if (s.length <= maxLen) return s;
  return `${s.slice(0, maxLen - 1)}…`;
}

const CITY_PHOTO_MISSING_SUB_EMPTY = 'В сервисе пока нет фотографий этого города';
const CITY_PHOTO_MISSING_SUB_FAILED =
  'Файл недоступен. Удалите снимок и загрузите другой или обновите страницу.';

function escapeHtmlText(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** HTML блока «Нет изображения» внутри кадра (клон из &lt;template&gt; на странице города). */
function getCityPhotoMissingInnerHtml(subtitle) {
  const tpl = document.getElementById('city-photo-carousel-missing-inner-template');
  if (!(tpl instanceof HTMLTemplateElement)) {
    return `<div class="city-photo-missing-inner absolute inset-0 flex flex-col items-center justify-center gap-2 px-4 py-6 text-center"><p class="text-base font-semibold text-neutral-800 dark:text-neutral-100">Нет изображения</p><p class="city-photo-missing-subtitle max-w-sm text-sm text-neutral-600 dark:text-neutral-400">${escapeHtmlText(subtitle)}</p></div>`;
  }
  const host = document.createElement('div');
  host.appendChild(tpl.content.cloneNode(true));
  const sub = host.querySelector('.city-photo-missing-subtitle');
  if (sub) sub.textContent = subtitle;
  return host.innerHTML;
}

function replaceCityPhotoMainUserSlideWithMissing(slide) {
  if (!(slide instanceof HTMLElement)) return;
  if (!(slide.getAttribute('data-photo-id') || '').length) return;
  slide.innerHTML = `<div class="block w-full"><div class="${CITY_PHOTO_STAGE_CLASS}">${getCityPhotoMissingInnerHtml(CITY_PHOTO_MISSING_SUB_FAILED)}</div></div>`;
  slide.setAttribute('data-is-image-unavailable', 'true');
}

function replaceCityPhotoThumbWithMissing(img) {
  if (!(img instanceof HTMLImageElement)) return;
  const slide = img.closest('.swiper-slide');
  if (!(slide instanceof HTMLElement)) return;
  slide.innerHTML = `<div class="flex h-full w-full flex-col items-center justify-center gap-0.5 bg-neutral-200/70 px-1 text-center dark:bg-neutral-700/55" role="img" aria-label="Превью недоступно">
    <svg xmlns="http://www.w3.org/2000/svg" class="size-4 shrink-0 text-neutral-500 dark:text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3A1.5 1.5 0 0 0 1.5 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008H12V8.25Z"/></svg>
    <span class="text-[9px] font-medium leading-tight text-neutral-600 dark:text-neutral-400">Нет фото</span>
  </div>`;
}

function bindCityPhotoUserMediaErrorHandlers(citySwiper, thumbsElement, syncControlsWithActiveSlide) {
  const onMainFail = (slide) => {
    replaceCityPhotoMainUserSlideWithMissing(slide);
    initCityGallery();
    if (citySwiper) {
      bindCityMainSwiperImagesForAutoHeight(citySwiper);
      citySwiper.update();
    }
    syncControlsWithActiveSlide();
  };

  citySwiper?.el?.querySelectorAll('img.city-photo-main-img').forEach((img) => {
    if (!(img instanceof HTMLImageElement)) return;
    if (img.dataset.cityPhotoErrorBound === '1') return;
    img.dataset.cityPhotoErrorBound = '1';
    const run = () => {
      const slide = img.closest('.swiper-slide');
      if (!(slide instanceof HTMLElement)) return;
      if (!(slide.getAttribute('data-photo-id') || '').length) return;
      onMainFail(slide);
    };
    img.addEventListener('error', run, { once: true });
    if (img.complete && img.naturalWidth === 0 && img.naturalHeight === 0) {
      run();
    }
  });

  thumbsElement?.querySelectorAll('img.city-photo-thumb-img').forEach((img) => {
    if (!(img instanceof HTMLImageElement)) return;
    if (img.dataset.cityPhotoThumbErrorBound === '1') return;
    img.dataset.cityPhotoThumbErrorBound = '1';
    const run = () => replaceCityPhotoThumbWithMissing(img);
    img.addEventListener('error', run, { once: true });
    if (img.complete && img.naturalWidth === 0 && img.naturalHeight === 0) {
      run();
    }
  });
}

function setCityCarouselNavVisible(visible, prev, next, pag) {
  [prev, next, pag].forEach((el) => {
    if (el instanceof HTMLElement) {
      el.classList.toggle('hidden', !visible);
    }
  });
}

/** Индекс слайда с фото по умолчанию (`data-is-default`), иначе 0. */
function getCityPhotoMainInitialSlideIndex(swiperEl) {
  if (!(swiperEl instanceof HTMLElement)) return 0;
  const slides = [...swiperEl.querySelectorAll('.swiper-slide')];
  const i = slides.findIndex((s) => s.getAttribute('data-is-default') === 'true');
  return i >= 0 ? i : 0;
}

function getCityPhotoThumbDefaultBadgeMarkup(isDefault) {
  return `<span class="city-photo-thumb-default-badge pointer-events-none absolute bottom-0.5 right-0.5 inline-grid size-5 place-items-center rounded-full border border-white/40 bg-black/55 leading-none text-white shadow-md backdrop-blur-[2px] ${
    isDefault ? '' : 'hidden'
  }" role="img" aria-label="Основное фото" title="Основное фото" aria-hidden="${isDefault ? 'false' : 'true'}"><svg xmlns="http://www.w3.org/2000/svg" class="block size-3.5 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.704 5.29a1 1 0 010 1.42l-7.2 7.2a1 1 0 01-1.415 0l-3-3a1 1 0 111.414-1.42l2.293 2.294 6.493-6.494a1 1 0 011.415 0z" clip-rule="evenodd"/></svg></span>`;
}

function updateCityPhotoThumbDefaultBadges(thumbsRoot) {
  if (!(thumbsRoot instanceof HTMLElement)) return;
  thumbsRoot.querySelectorAll('.swiper-slide[data-photo-id]').forEach((slide) => {
    const pid = slide.getAttribute('data-photo-id') || '';
    if (!pid.length) return;
    const badge = slide.querySelector('.city-photo-thumb-default-badge');
    if (!(badge instanceof HTMLElement)) return;
    const isDef = slide.getAttribute('data-is-default') === 'true';
    badge.classList.toggle('hidden', !isDef);
    badge.setAttribute('aria-hidden', isDef ? 'false' : 'true');
  });
}

/** Синхронизация `data-is-default` на главной карусели и превью после ответа API. */
function applyCityPhotoDefaultFromServer(citySwiper, defaultPhotoId, thumbsElement) {
  const defaultId = defaultPhotoId == null ? null : String(defaultPhotoId);
  const patchSlides = (root) => {
    if (!(root instanceof HTMLElement)) return;
    root.querySelectorAll('.swiper-slide[data-photo-id]').forEach((slide) => {
      const pid = slide.getAttribute('data-photo-id') || '';
      if (!pid.length) return;
      slide.setAttribute(
        'data-is-default',
        defaultId !== null && pid === defaultId ? 'true' : 'false',
      );
    });
  };
  if (citySwiper?.el) patchSlides(citySwiper.el);
  if (thumbsElement instanceof HTMLElement) {
    patchSlides(thumbsElement);
    updateCityPhotoThumbDefaultBadges(thumbsElement);
  }
}

/** Пересчёт высоты после загрузки картинок (Swiper `autoHeight`). */
function bindCityMainSwiperImagesForAutoHeight(swiper) {
  if (!swiper?.el) return;
  const speed = swiper.params.speed ?? 300;
  const bump = () => swiper.updateAutoHeight(speed);
  swiper.el.querySelectorAll('img').forEach((img) => {
    if (!(img instanceof HTMLImageElement)) return;
    if (img.complete && img.naturalWidth > 0) {
      requestAnimationFrame(bump);
      return;
    }
    img.addEventListener('load', () => bump(), { once: true });
  });
}

/**
 * После удаления последнего пользовательского фото: плейсхолдер в карусели, скрыта панель превью, без перезагрузки страницы.
 * Вызывающий обязан присвоить `thumbsSwiper = null` после вызова (связь thumbs с main сбрасывается).
 */
function showPlaceholderAfterLastCityPhotoRemoved(citySwiper, thumbsSwiperInstance, ctx) {
  const { thumbsPanel, thumbsElement, prevButton, nextButton, pagination } = ctx;

  if (thumbsSwiperInstance) {
    try {
      thumbsSwiperInstance.destroy(true, true);
    } catch {
      /* Swiper уже уничтожен */
    }
  }
  citySwiper.params.thumbs = undefined;

  hideCityPhotoThumbsPanel(thumbsPanel);
  if (thumbsElement instanceof HTMLElement) {
    const wrapper = thumbsElement.querySelector('.swiper-wrapper');
    if (wrapper) {
      wrapper.innerHTML = '';
    }
  }

  const placeholderSlideHtml = `
    <div class="swiper-slide !h-auto"
         data-photo-id=""
         data-is-default="true"
         data-is-placeholder="true">
      <div class="${CITY_PHOTO_STAGE_PLACEHOLDER_CLASS}">
        ${getCityPhotoMissingInnerHtml(CITY_PHOTO_MISSING_SUB_EMPTY)}
      </div>
    </div>`;

  citySwiper.appendSlide(placeholderSlideHtml);
  citySwiper.update();
  bindCityMainSwiperImagesForAutoHeight(citySwiper);
  citySwiper.slideTo(0, 0);
  setCityCarouselNavVisible(false, prevButton, nextButton, pagination);
  showCityPhotoNoImageMessages();
}

function initCityPhotoManager() {
  const uploadForm = document.getElementById('city-photo-upload-form');
  const list = document.getElementById('city-photo-list');
  const fileInput = document.getElementById('city-photo-file-input');
  const uploadSubmit = document.getElementById('city-photo-upload-submit');
  const uploadSpinner = document.getElementById('city-photo-upload-spinner');
  const uploadText = document.getElementById('city-photo-upload-text');
  const uploadProgress = document.getElementById('city-photo-upload-progress');
  const uploadProgressLabel = document.getElementById('city-photo-upload-progress-text');
  const uploadProgressSpinnerEl = document.getElementById('city-photo-upload-progress-spinner');
  const deleteButton = document.getElementById('city-photo-delete-btn');
  const deleteSpinner = document.getElementById('city-photo-delete-spinner');
  const deleteText = document.getElementById('city-photo-delete-text');
  const carouselRoot = document.querySelector('.city-image-carousel');
  if (!(carouselRoot instanceof HTMLElement)) {
    return;
  }
  const setDefaultButton = document.getElementById('city-photo-set-default-btn');
  const setDefaultSpinner = document.getElementById('city-photo-set-default-spinner');
  const setDefaultText = document.getElementById('city-photo-set-default-text');
  const defaultLabel = document.getElementById('city-photo-default-label');
  const serviceLabel = document.getElementById('city-photo-service-label');
  const thumbsPanel = document.getElementById('city-photo-thumbs-panel');
  const swiperElement = carouselRoot?.querySelector('.city-photo-swiper');
  const thumbsElement = carouselRoot?.parentElement?.querySelector('.city-photo-thumbs') || null;
  const prevButton = carouselRoot?.querySelector('.city-swiper-prev');
  const nextButton = carouselRoot?.querySelector('.city-swiper-next');
  const pagination = carouselRoot?.querySelector('.city-swiper-pagination');

  const initialMainSlide =
    swiperElement instanceof HTMLElement ? getCityPhotoMainInitialSlideIndex(swiperElement) : 0;

  let thumbsSwiper = null;
  if (
    thumbsElement instanceof HTMLElement &&
    thumbsPanel instanceof HTMLElement &&
    !isCityPhotoThumbsPanelHidden(thumbsPanel)
  ) {
    thumbsSwiper = new Swiper(thumbsElement, {
      modules: [FreeMode, Manipulation],
      spaceBetween: 8,
      slidesPerView: 'auto',
      centerInsufficientSlides: true,
      freeMode: true,
      watchSlidesProgress: true,
      initialSlide: initialMainSlide,
    });
  }

  let citySwiper = null;
  if (swiperElement instanceof HTMLElement) {
    citySwiper = new Swiper(swiperElement, {
      modules: [Navigation, Pagination, Manipulation, Thumbs],
      slidesPerView: 1,
      speed: 300,
      autoHeight: true,
      initialSlide: initialMainSlide,
      navigation: {
        prevEl: prevButton instanceof HTMLElement ? prevButton : null,
        nextEl: nextButton instanceof HTMLElement ? nextButton : null,
      },
      pagination: {
        el: pagination instanceof HTMLElement ? pagination : null,
        clickable: true,
        dynamicBullets: true,
      },
      thumbs: thumbsSwiper
        ? { swiper: thumbsSwiper, multipleActiveThumbs: false }
        : undefined,
    });
    bindCityMainSwiperImagesForAutoHeight(citySwiper);
  }

  const syncControlsWithActiveSlide = () => {
    if (!list) return;
    if (!citySwiper || citySwiper.slides.length === 0) return;
    const activeSlide = citySwiper.slides[citySwiper.activeIndex];
    if (!activeSlide) return;

    const photoId = activeSlide.getAttribute('data-photo-id') || '';
    const isDefault = activeSlide.getAttribute('data-is-default') === 'true';
    const isServiceImage = activeSlide.getAttribute('data-is-service-image') === 'true';
    const isPlaceholder = activeSlide.getAttribute('data-is-placeholder') === 'true';
    const isManageable = photoId.length > 0;
    list.setAttribute('data-photo-id', photoId);

    if (setDefaultButton) {
      setDefaultButton.classList.toggle('hidden', isDefault || !isManageable || isServiceImage || isPlaceholder);
    }
    if (defaultLabel) {
      defaultLabel.classList.toggle('hidden', !isDefault || !isManageable || isServiceImage || isPlaceholder);
    }
    if (serviceLabel) {
      serviceLabel.classList.toggle('hidden', !isServiceImage);
    }
    if (deleteButton) {
      deleteButton.classList.toggle('hidden', !isManageable || isServiceImage || isPlaceholder);
    }
  };

  if (citySwiper) {
    bindCityPhotoUserMediaErrorHandlers(citySwiper, thumbsElement, syncControlsWithActiveSlide);

    /**
     * `city.image` недоступен (404 и т.п.): убираем слайд сервиса и его превью.
     * Если есть фото пользователя — только они; если нет — плейсхолдер и скрытая панель миниатюр.
     */
    const onBrokenServiceImage = () => {
      const serviceSlide = citySwiper.el.querySelector('.swiper-slide[data-is-service-image="true"]');
      if (!(serviceSlide instanceof HTMLElement)) return;
      const serviceIndex = Array.from(citySwiper.slides).indexOf(serviceSlide);
      if (serviceIndex < 0) return;

      const hasUserPhotos = Array.from(citySwiper.slides).some(
        (s, idx) => idx !== serviceIndex && (s.getAttribute('data-photo-id') || '').length > 0,
      );

      if (hasUserPhotos) {
        citySwiper.removeSlide(serviceIndex);
        if (thumbsSwiper) {
          const tIdx = Array.from(thumbsSwiper.slides).findIndex(
            (s) => s.getAttribute('data-is-service-image') === 'true',
          );
          if (tIdx >= 0) {
            thumbsSwiper.removeSlide(tIdx);
          }
          thumbsSwiper.update();
        }
        citySwiper.thumbs?.update?.(true);
        const navVisible = citySwiper.slides.length > 1;
        setCityCarouselNavVisible(navVisible, prevButton, nextButton, pagination);
        const idx = Math.min(serviceIndex, citySwiper.slides.length - 1);
        citySwiper.slideTo(Math.max(0, idx), 0);
      } else {
        citySwiper.removeSlide(serviceIndex);
        showPlaceholderAfterLastCityPhotoRemoved(citySwiper, thumbsSwiper, {
          thumbsPanel,
          thumbsElement,
          prevButton,
          nextButton,
          pagination,
        });
        thumbsSwiper = null;
      }

      initCityGallery();
      bindCityMainSwiperImagesForAutoHeight(citySwiper);
      citySwiper.update();
      syncControlsWithActiveSlide();
    };

    const wireServiceImageError = (img) => {
      if (!(img instanceof HTMLImageElement)) return;
      img.addEventListener('error', () => onBrokenServiceImage(), { once: true });
      if (img.complete && img.naturalWidth === 0 && img.naturalHeight === 0) {
        onBrokenServiceImage();
      }
    };

    wireServiceImageError(citySwiper.el.querySelector('.swiper-slide[data-is-service-image="true"] img'));
    wireServiceImageError(
      thumbsElement?.querySelector('.swiper-slide[data-is-service-image="true"] img') ?? null,
    );

    citySwiper.on('slideChange', syncControlsWithActiveSlide);
  }

  syncControlsWithActiveSlide();

  if (citySwiper) {
    const alignMainToDefaultSlide = () => {
      const target = getCityPhotoMainInitialSlideIndex(citySwiper.el);
      citySwiper.slideTo(target, 0, false);
      thumbsSwiper?.slideTo(target, 0);
      citySwiper.thumbs?.update?.(true);
      syncControlsWithActiveSlide();
    };
    requestAnimationFrame(() => {
      alignMainToDefaultSlide();
      requestAnimationFrame(alignMainToDefaultSlide);
    });
  }

  if (!uploadForm) {
    return;
  }

  const setLoadingState = (isLoading, action = null, progressMessage = null) => {
    if (fileInput instanceof HTMLInputElement) {
      fileInput.disabled = isLoading;
    }
    if (uploadSubmit instanceof HTMLButtonElement) {
      uploadSubmit.disabled = isLoading;
    }
    if (setDefaultButton instanceof HTMLButtonElement) {
      setDefaultButton.disabled = isLoading;
    }
    if (deleteButton instanceof HTMLButtonElement) {
      deleteButton.disabled = isLoading;
    }

    if (uploadSpinner instanceof HTMLElement) {
      uploadSpinner.classList.toggle('hidden', !(isLoading && action === 'upload'));
    }
    if (uploadText instanceof HTMLElement) {
      uploadText.textContent = isLoading && action === 'upload' ? 'Загрузка...' : 'Загрузить';
    }
    if (uploadProgress instanceof HTMLElement) {
      if (isLoading && action === 'upload' && typeof progressMessage === 'string' && progressMessage.length > 0) {
        if (uploadProgressLabel instanceof HTMLElement) {
          uploadProgressLabel.textContent = progressMessage;
        }
        uploadProgress.classList.remove('hidden');
        if (uploadProgressSpinnerEl instanceof HTMLElement) {
          uploadProgressSpinnerEl.classList.remove('hidden');
        }
      } else {
        if (uploadProgressLabel instanceof HTMLElement) {
          uploadProgressLabel.textContent = '';
        }
        uploadProgress.classList.add('hidden');
        if (uploadProgressSpinnerEl instanceof HTMLElement) {
          uploadProgressSpinnerEl.classList.add('hidden');
        }
      }
    }
    if (setDefaultSpinner instanceof HTMLElement) {
      setDefaultSpinner.classList.toggle('hidden', !(isLoading && action === 'set-default'));
    }
    if (setDefaultText instanceof HTMLElement) {
      setDefaultText.textContent = isLoading && action === 'set-default' ? 'Сохраняем...' : 'Сделать основным';
    }
    if (deleteSpinner instanceof HTMLElement) {
      deleteSpinner.classList.toggle('hidden', !(isLoading && action === 'delete'));
    }
    if (deleteText instanceof HTMLElement) {
      deleteText.textContent = isLoading && action === 'delete' ? 'Удаляем...' : 'Удалить';
    }
  };

  const integrateUploadedPhotoIntoCarousel = (uploadedPhoto) => {
    const uploadedId = uploadedPhoto?.id;
    if (!citySwiper || !uploadedId) return false;

    const imageHref =
      typeof uploadedPhoto.image_url === 'string' && uploadedPhoto.image_url.length > 0
        ? uploadedPhoto.image_url
        : `/api/city/photos/${uploadedId}/`;
    const uploadedIsDefault = Boolean(uploadedPhoto.is_default);
    const thumbHtml = `
            <button type="button" class="${CITY_PHOTO_THUMB_SLIDE_BASE_CLASS}" data-photo-id="${uploadedId}" data-is-default="${uploadedIsDefault ? 'true' : 'false'}" aria-label="Показать фото">
              <img src="${imageHref}"
                   alt="Миниатюра фото города"
                   loading="lazy"
                   decoding="async"
                   class="city-photo-thumb-img h-full w-full object-cover">
              ${getCityPhotoThumbDefaultBadgeMarkup(uploadedIsDefault)}
            </button>
          `;

    const thumbsWasHidden =
      thumbsPanel instanceof HTMLElement && isCityPhotoThumbsPanelHidden(thumbsPanel);

    const placeholderIndex = Array.from(citySwiper.slides).findIndex(
      (slide) => slide.getAttribute('data-is-placeholder') === 'true',
    );
    if (placeholderIndex >= 0) {
      citySwiper.removeSlide(placeholderIndex);
    }

    const slideHtml = `
          <div class="swiper-slide !h-auto" data-photo-id="${uploadedId}" data-is-default="${uploadedPhoto.is_default ? 'true' : 'false'}">
            <a href="${imageHref}" class="city-glightbox block w-full" data-type="image">
              <div class="${CITY_PHOTO_STAGE_CLASS}">
                <img src="${imageHref}"
                     alt="Фото города"
                     loading="lazy"
                     decoding="async"
                     class="city-photo-main-img absolute inset-0 h-full w-full object-contain">
              </div>
            </a>
          </div>
        `;
    const serviceSlideIndex = Array.from(citySwiper.slides).findIndex(
      (slide) => slide.getAttribute('data-is-service-image') === 'true',
    );
    if (serviceSlideIndex >= 0) {
      citySwiper.addSlide(serviceSlideIndex, slideHtml);
    } else {
      citySwiper.appendSlide(slideHtml);
    }

    if (
      thumbsWasHidden &&
      thumbsElement instanceof HTMLElement &&
      thumbsPanel instanceof HTMLElement
    ) {
      showCityPhotoThumbsPanel(thumbsPanel);
      const thumbsWrapper = thumbsElement.querySelector('.swiper-wrapper');
      if (thumbsWrapper) {
        thumbsWrapper.insertAdjacentHTML('beforeend', thumbHtml);
      }
      thumbsSwiper = new Swiper(thumbsElement, {
        modules: [FreeMode, Manipulation],
        spaceBetween: 8,
        slidesPerView: 'auto',
        centerInsufficientSlides: true,
        freeMode: true,
        watchSlidesProgress: true,
      });
      citySwiper.params.thumbs = { swiper: thumbsSwiper, multipleActiveThumbs: false };
      citySwiper.thumbs.init();
      citySwiper.thumbs.update(true);
    } else if (thumbsSwiper) {
      const placeholderThumbIndex = Array.from(thumbsSwiper.slides).findIndex(
        (slide) => slide.getAttribute('data-is-placeholder') === 'true',
      );
      if (placeholderThumbIndex >= 0) {
        thumbsSwiper.removeSlide(placeholderThumbIndex);
      }
      const serviceThumbIndex = Array.from(thumbsSwiper.slides).findIndex(
        (slide) => slide.getAttribute('data-is-service-image') === 'true',
      );
      if (serviceThumbIndex >= 0) {
        thumbsSwiper.addSlide(serviceThumbIndex, thumbHtml);
      } else {
        thumbsSwiper.appendSlide(thumbHtml);
      }
      thumbsSwiper.update();
    }

    citySwiper.update();
    bindCityMainSwiperImagesForAutoHeight(citySwiper);
    const newSlideIndex = Array.from(citySwiper.slides).findIndex(
      (slide) => slide.getAttribute('data-photo-id') === String(uploadedId),
    );
    if (newSlideIndex >= 0) {
      citySwiper.slideTo(newSlideIndex, 0);
    }
    if (thumbsSwiper) {
      const syncThumbsWithMain = () => {
        const i = citySwiper.activeIndex;
        thumbsSwiper.slideTo(i, 0);
        citySwiper.thumbs?.update?.(true);
      };
      syncThumbsWithMain();
      requestAnimationFrame(syncThumbsWithMain);
    }
    syncControlsWithActiveSlide();
    initCityGallery();
    bindCityPhotoUserMediaErrorHandlers(citySwiper, thumbsElement, syncControlsWithActiveSlide);
    hideCityPhotoNoImageMessages();
    return true;
  };

  uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(uploadForm);
    const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');
    const cityId = formData.get('city_id');

    const fileInputEl = uploadForm.querySelector('#city-photo-file-input');
    const fileList =
      fileInputEl instanceof HTMLInputElement && fileInputEl.files ? fileInputEl.files : null;
    const files = fileList ? Array.from(fileList).filter((f) => f instanceof File && f.size > 0) : [];

    if (files.length === 0) {
      showError('Выберите одно или несколько изображений для загрузки');
      return;
    }

    const existingCount = citySwiper ? countCityUserPhotosInCarousel(citySwiper) : 0;
    const slotsLeft = Math.max(0, MAX_CITY_USER_PHOTOS - existingCount);
    if (slotsLeft === 0) {
      showError(`Уже загружено максимум фотографий (${MAX_CITY_USER_PHOTOS} шт.) для этого города`);
      return;
    }

    const filesToUpload = files.slice(0, slotsLeft);
    if (files.length > slotsLeft) {
      showCityPhotoUploadNotice(
        `Будет загружено ${slotsLeft} из ${files.length} файлов (лимит ${MAX_CITY_USER_PHOTOS} фото на город).`,
      );
    }

    try {
      let anyCarouselUpdate = false;
      for (let i = 0; i < filesToUpload.length; i += 1) {
        const file = filesToUpload[i];
        const shortName = truncateCityPhotoFileName(file.name);
        const progressMessage =
          filesToUpload.length > 1
            ? `Загрузка файла ${i + 1} из ${filesToUpload.length} на сервер: «${shortName}» — подождите…`
            : `Отправка фото на сервер: «${shortName}» — подождите…`;
        setLoadingState(true, 'upload', progressMessage);
        const fd = new FormData();
        fd.append('csrfmiddlewaretoken', String(csrfToken ?? ''));
        if (cityId != null) fd.append('city_id', String(cityId));
        fd.append('image', file, file.name);

        const response = await fetch('/api/city/photos/upload/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
          },
          body: fd,
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || 'Не удалось загрузить фото');
        }
        const uploadedPhoto = data?.photo;
        if (citySwiper && uploadedPhoto?.id) {
          integrateUploadedPhotoIntoCarousel(uploadedPhoto);
          anyCarouselUpdate = true;
        } else {
          showError('Фото загружено. Обновите страницу для отображения в карусели.');
          break;
        }
      }

      if (anyCarouselUpdate) {
        hideCityPhotoUploadMessage();
      }
      uploadForm.reset();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Не удалось загрузить фото';
      showError(message);
    } finally {
      setLoadingState(false);
    }
  });

  if (!list) return;
  list.addEventListener('click', async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const deleteTrigger = target.closest('.city-photo-delete');
    const setDefaultTrigger = target.closest('.city-photo-set-default');

    const item = target.closest('[data-photo-id]');
    if (!item) return;
    const photoId = item.getAttribute('data-photo-id');
    if (!photoId) return;

    const csrfToken = getCookie('csrftoken');
    if (deleteTrigger) {
      event.preventDefault();
      const confirmed = await openConfirmModal({
        title: 'Удаление фото',
        message: 'Вы уверены, что хотите удалить это изображение? Его нельзя будет восстановить.',
        confirmLabel: 'Удалить',
        cancelLabel: 'Отмена',
      });
      if (!confirmed) {
        return;
      }

      setLoadingState(true, 'delete');
      try {
        const response = await fetch(`/api/city/photos/${photoId}/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': csrfToken,
          },
        });
        const deletePayload = await response.json();
        if (!response.ok) {
          throw new Error(deletePayload.detail || 'Не удалось удалить фото');
        }

        if (citySwiper) {
          const activeIndex = citySwiper.activeIndex;
          citySwiper.removeSlide(activeIndex);
          citySwiper.update();

          if (citySwiper.slides.length === 0) {
            showPlaceholderAfterLastCityPhotoRemoved(citySwiper, thumbsSwiper, {
              thumbsPanel,
              thumbsElement,
              prevButton,
              nextButton,
              pagination,
            });
            thumbsSwiper = null;
          } else {
            if (thumbsSwiper) {
              const thumbIndex = Array.from(thumbsSwiper.slides).findIndex(
                (s) => (s.getAttribute('data-photo-id') || '') === photoId,
              );
              if (thumbIndex >= 0) {
                thumbsSwiper.removeSlide(thumbIndex);
              }
              thumbsSwiper.update();
            }

            applyCityPhotoDefaultFromServer(citySwiper, deletePayload.default_photo_id, thumbsElement);
            const nextIndex = Math.min(activeIndex, citySwiper.slides.length - 1);
            citySwiper.slideTo(nextIndex, 0);
            if (thumbsSwiper) {
              const syncThumbsWithMain = () => {
                const i = citySwiper.activeIndex;
                thumbsSwiper.slideTo(i, 0);
                citySwiper.thumbs?.update?.(true);
              };
              syncThumbsWithMain();
              requestAnimationFrame(syncThumbsWithMain);
            }
          }
          syncControlsWithActiveSlide();
          initCityGallery();
        } else {
          window.location.reload();
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Не удалось удалить фото';
        showError(message);
      } finally {
        setLoadingState(false);
      }
    }

    if (setDefaultTrigger) {
      event.preventDefault();
      setLoadingState(true, 'set-default');
      try {
        const response = await fetch(`/api/city/photos/${photoId}/default/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
          },
        });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Не удалось выбрать фото по умолчанию');
        }

        if (citySwiper) {
          applyCityPhotoDefaultFromServer(citySwiper, photoId, thumbsElement);
          syncControlsWithActiveSlide();
        } else {
          window.location.reload();
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Не удалось выбрать фото по умолчанию';
        showError(message);
      } finally {
        setLoadingState(false);
      }
    }
  });
}

function initCityStandardPhotoForm() {
  const form = document.getElementById('city-standard-photo-form');
  if (!(form instanceof HTMLFormElement)) return;

  const submitBtn = document.getElementById('city-standard-photo-submit');
  const spinner = document.getElementById('city-standard-photo-spinner');
  const submitText = document.getElementById('city-standard-photo-submit-text');
  const errorEl = document.getElementById('city-standard-photo-error');

  const setLoading = (loading) => {
    if (submitBtn instanceof HTMLButtonElement) submitBtn.disabled = loading;
    spinner?.classList.toggle('hidden', !loading);
    if (submitText) submitText.textContent = loading ? 'Сохранение…' : 'Сохранить';
  };

  const showError = (message) => {
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.classList.remove('hidden');
    }
  };

  const hideError = () => {
    errorEl?.classList.add('hidden');
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const csrfToken = getCookie('csrftoken');
    if (!csrfToken) {
      showError('Нет CSRF-токена. Обновите страницу.');
      return;
    }

    const body = new FormData(form);
    setLoading(true);
    try {
      const response = await fetch('/api/city/standard_photo/upload/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
        },
        body,
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = data.detail;
        if (typeof detail === 'string') {
          showError(detail);
        } else if (data && typeof data === 'object') {
          const parts = [];
          for (const v of Object.values(data)) {
            if (Array.isArray(v)) parts.push(...v.map(String));
            else if (typeof v === 'string') parts.push(v);
          }
          showError(parts.join(' ') || 'Не удалось сохранить');
        } else {
          showError('Не удалось сохранить');
        }
        return;
      }

      window.location.reload();
    } catch {
      showError('Ошибка сети');
    } finally {
      setLoading(false);
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initCityGallery();
    initCityPhotoManager();
    initCityStandardPhotoForm();
  });
} else {
  initCityGallery();
  initCityPhotoManager();
  initCityStandardPhotoForm();
}
