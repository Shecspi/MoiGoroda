import GLightbox from 'glightbox';
import 'glightbox/dist/css/glightbox.min.css';
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

function initCityGallery() {
  const galleryLinks = document.querySelectorAll('.city-glightbox');
  if (galleryLinks.length === 0) return;

  if (lightboxInstance) {
    lightboxInstance.destroy();
  }

  lightboxInstance = GLightbox({
    selector: '.city-glightbox',
    touchNavigation: true,
    loop: true,
    autoplayVideos: false,
  });
}

function showError(message) {
  const errorNode = document.getElementById('city-photo-error');
  if (!errorNode) return;
  errorNode.textContent = message;
  errorNode.classList.remove('hidden');
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

const CITY_PHOTO_STAGE_CLASS =
  'city-photo-stage relative mx-auto w-[min(100%,calc(min(85vh,600px)*16/9))] aspect-video overflow-hidden rounded-lg bg-neutral-300/85 shadow-inner ring-1 ring-neutral-400/25 backdrop-blur-md dark:bg-neutral-800/65 dark:ring-white/15';

const CITY_PHOTO_THUMB_SLIDE_BASE_CLASS =
  'swiper-slide relative !w-20 !h-14 rounded-md overflow-hidden border border-layer-line bg-layer cursor-pointer opacity-50 transition-opacity duration-200 ease-out [&.swiper-slide-thumb-active]:opacity-100';

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
      <div class="${CITY_PHOTO_STAGE_CLASS} pointer-events-none select-none">
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

  const setLoadingState = (isLoading, action = null) => {
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

  uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(uploadForm);
    const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');
    const imageFile = formData.get('image');
    if (!(imageFile instanceof File) || imageFile.size === 0) {
      showError('Выберите изображение для загрузки');
      return;
    }

    setLoadingState(true, 'upload');

    try {
      const response = await fetch('/api/city/photos/upload/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
        },
        body: formData,
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Не удалось загрузить фото');
      }
      const data = await response.json();
      const uploadedPhoto = data?.photo;
      const uploadedId = uploadedPhoto?.id;

      if (citySwiper && uploadedId) {
        const imageHref = `/api/city/photos/${uploadedId}/`;
        const uploadedIsDefault = Boolean(uploadedPhoto.is_default);
        const thumbHtml = `
            <div class="${CITY_PHOTO_THUMB_SLIDE_BASE_CLASS}" data-photo-id="${uploadedId}" data-is-default="${uploadedIsDefault ? 'true' : 'false'}">
              <img src="${imageHref}"
                   alt="Миниатюра фото города"
                   class="city-photo-thumb-img h-full w-full object-cover">
              ${getCityPhotoThumbDefaultBadgeMarkup(uploadedIsDefault)}
            </div>
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
              <div class="city-photo-stage relative mx-auto w-[min(100%,calc(min(85vh,600px)*16/9))] aspect-video overflow-hidden rounded-lg bg-neutral-300/85 shadow-inner ring-1 ring-neutral-400/25 backdrop-blur-md dark:bg-neutral-800/65 dark:ring-white/15">
                <img src="${imageHref}"
                     alt="Фото города"
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
            freeMode: true,
            watchSlidesProgress: true,
          });
          citySwiper.params.thumbs = { swiper: thumbsSwiper };
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
        syncControlsWithActiveSlide();
        initCityGallery();
        bindCityPhotoUserMediaErrorHandlers(citySwiper, thumbsElement, syncControlsWithActiveSlide);
        hideCityPhotoNoImageMessages();
      } else {
        // Если блок карусели отсутствует в текущем DOM, просим перезагрузить вручную.
        showError('Фото загружено. Обновите страницу для отображения в карусели.');
      }

      const errorNode = document.getElementById('city-photo-error');
      if (errorNode) {
        errorNode.classList.add('hidden');
        errorNode.textContent = '';
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
              const thumbToRemove = thumbsSwiper.el.querySelector(
                `.swiper-slide[data-photo-id="${photoId}"]`,
              );
              if (thumbToRemove) {
                thumbToRemove.remove();
              }
              thumbsSwiper.update();
            }

            applyCityPhotoDefaultFromServer(citySwiper, deletePayload.default_photo_id, thumbsElement);
            const nextIndex = Math.min(activeIndex, citySwiper.slides.length - 1);
            citySwiper.slideTo(nextIndex, 0);
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

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initCityGallery();
    initCityPhotoManager();
  });
} else {
  initCityGallery();
  initCityPhotoManager();
}
