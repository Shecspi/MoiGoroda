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

function initCityPhotoManager() {
  const uploadForm = document.getElementById('city-photo-upload-form');
  if (!uploadForm) return;
  const list = document.getElementById('city-photo-list');
  const fileInput = document.getElementById('city-photo-file-input');
  const uploadSubmit = document.getElementById('city-photo-upload-submit');
  const uploadSpinner = document.getElementById('city-photo-upload-spinner');
  const uploadText = document.getElementById('city-photo-upload-text');
  const deleteButton = document.getElementById('city-photo-delete-btn');
  const deleteSpinner = document.getElementById('city-photo-delete-spinner');
  const deleteText = document.getElementById('city-photo-delete-text');
  const carouselRoot = document.querySelector('.city-image-carousel');
  const setDefaultButton = document.getElementById('city-photo-set-default-btn');
  const setDefaultSpinner = document.getElementById('city-photo-set-default-spinner');
  const setDefaultText = document.getElementById('city-photo-set-default-text');
  const defaultLabel = document.getElementById('city-photo-default-label');
  const serviceLabel = document.getElementById('city-photo-service-label');
  const missingLabel = document.getElementById('city-photo-missing-label');
  const thumbsPanel = document.getElementById('city-photo-thumbs-panel');
  const swiperElement = carouselRoot?.querySelector('.city-photo-swiper');
  const thumbsElement = carouselRoot?.parentElement?.querySelector('.city-photo-thumbs') || null;
  const prevButton = carouselRoot?.querySelector('.city-swiper-prev');
  const nextButton = carouselRoot?.querySelector('.city-swiper-next');
  const pagination = carouselRoot?.querySelector('.city-swiper-pagination');

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
    });
  }

  let citySwiper = null;
  if (swiperElement instanceof HTMLElement) {
    citySwiper = new Swiper(swiperElement, {
      modules: [Navigation, Pagination, Manipulation, Thumbs],
      slidesPerView: 1,
      speed: 300,
      navigation: {
        prevEl: prevButton instanceof HTMLElement ? prevButton : null,
        nextEl: nextButton instanceof HTMLElement ? nextButton : null,
      },
      pagination: {
        el: pagination instanceof HTMLElement ? pagination : null,
        clickable: true,
        dynamicBullets: true,
      },
      thumbs: thumbsSwiper ? { swiper: thumbsSwiper } : undefined,
    });
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
    if (missingLabel) {
      missingLabel.classList.toggle('hidden', !isPlaceholder);
    }
    if (deleteButton) {
      deleteButton.classList.toggle('hidden', !isManageable || isServiceImage || isPlaceholder);
    }
  };

  syncControlsWithActiveSlide();
  if (citySwiper) {
    citySwiper.on('slideChange', syncControlsWithActiveSlide);
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
        const thumbHtml = `
            <div class="swiper-slide !w-20 !h-14 rounded-md overflow-hidden border border-layer-line bg-layer cursor-pointer" data-photo-id="${uploadedId}">
              <img src="${imageHref}"
                   alt="Миниатюра фото города"
                   class="w-full h-full object-cover"
                   onerror="this.onerror=null;this.src='/static/image/city_placeholder.png'">
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
          <div class="swiper-slide h-full" data-photo-id="${uploadedId}" data-is-default="${uploadedPhoto.is_default ? 'true' : 'false'}">
            <a href="${imageHref}" class="city-glightbox inline-flex w-full h-full items-center justify-center">
              <img src="${imageHref}"
                   alt="Фото города"
                   class="block max-w-full max-h-full w-auto h-auto object-contain rounded-lg shadow-lg mx-auto"
                   onerror="this.onerror=null;this.src='/static/image/city_placeholder.png'">
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
        const newSlideIndex = Array.from(citySwiper.slides).findIndex(
          (slide) => slide.getAttribute('data-photo-id') === String(uploadedId),
        );
        if (newSlideIndex >= 0) {
          citySwiper.slideTo(newSlideIndex, 0);
        }
        syncControlsWithActiveSlide();
        initCityGallery();
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
      setLoadingState(true, 'delete');
      try {
        const response = await fetch(`/api/city/photos/${photoId}/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': csrfToken,
          },
        });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Не удалось удалить фото');
        }

        if (citySwiper) {
          const activeIndex = citySwiper.activeIndex;
          citySwiper.removeSlide(activeIndex);
          citySwiper.update();

          if (thumbsSwiper) {
            const thumbToRemove = thumbsSwiper.el.querySelector(`.swiper-slide[data-photo-id="${photoId}"]`);
            if (thumbToRemove) {
              thumbToRemove.remove();
            }
            thumbsSwiper.update();
          }

          if (citySwiper.slides.length === 0) {
            window.location.reload();
            return;
          }

          const nextIndex = Math.min(activeIndex, citySwiper.slides.length - 1);
          citySwiper.slideTo(nextIndex, 0);
          syncControlsWithActiveSlide();
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
          citySwiper.slides.forEach((slide) => {
            const slidePhotoId = slide.getAttribute('data-photo-id');
            const isTarget = slidePhotoId === photoId;
            slide.setAttribute('data-is-default', isTarget ? 'true' : 'false');
          });
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
