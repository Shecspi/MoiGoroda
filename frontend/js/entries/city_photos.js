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

function initCityPhotoManager() {
  const uploadForm = document.getElementById('city-photo-upload-form');
  if (!uploadForm) return;
  const list = document.getElementById('city-photo-list');
  const fileInput = document.getElementById('city-photo-file-input');
  const uploadSubmit = document.getElementById('city-photo-upload-submit');
  const uploadSpinner = document.getElementById('city-photo-upload-spinner');
  const uploadText = document.getElementById('city-photo-upload-text');
  const carouselRoot = document.querySelector('.city-image-carousel');
  const setDefaultButton = document.getElementById('city-photo-set-default-btn');
  const defaultLabel = document.getElementById('city-photo-default-label');
  const swiperElement = carouselRoot?.querySelector('.city-photo-swiper');
  const thumbsElement = carouselRoot?.parentElement?.querySelector('.city-photo-thumbs') || null;
  const prevButton = carouselRoot?.querySelector('.city-swiper-prev');
  const nextButton = carouselRoot?.querySelector('.city-swiper-next');
  const pagination = carouselRoot?.querySelector('.city-swiper-pagination');

  let thumbsSwiper = null;
  if (thumbsElement instanceof HTMLElement) {
    thumbsSwiper = new Swiper(thumbsElement, {
      modules: [FreeMode],
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
    list.setAttribute('data-photo-id', photoId);

    if (setDefaultButton) {
      setDefaultButton.classList.toggle('hidden', isDefault);
    }
    if (defaultLabel) {
      defaultLabel.classList.toggle('hidden', !isDefault);
    }
  };

  syncControlsWithActiveSlide();
  if (citySwiper) {
    citySwiper.on('slideChange', syncControlsWithActiveSlide);
  }

  uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(uploadForm);
    const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');
    const imageFile = formData.get('image');
    if (!(imageFile instanceof File) || imageFile.size === 0) {
      showError('Выберите изображение для загрузки');
      return;
    }

    if (fileInput instanceof HTMLInputElement) {
      fileInput.disabled = true;
    }
    if (uploadSubmit instanceof HTMLButtonElement) {
      uploadSubmit.disabled = true;
    }
    if (uploadSpinner instanceof HTMLElement) {
      uploadSpinner.classList.remove('hidden');
    }
    if (uploadText instanceof HTMLElement) {
      uploadText.textContent = 'Загрузка...';
    }

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
        citySwiper.prependSlide(slideHtml);

        if (thumbsSwiper) {
          const thumbHtml = `
            <div class="swiper-slide !w-20 !h-14 rounded-md overflow-hidden border border-layer-line bg-layer cursor-pointer">
              <img src="${imageHref}"
                   alt="Миниатюра фото города"
                   class="w-full h-full object-cover"
                   onerror="this.onerror=null;this.src='/static/image/city_placeholder.png'">
            </div>
          `;
          thumbsSwiper.prependSlide(thumbHtml);
          thumbsSwiper.update();
        }

        citySwiper.update();
        citySwiper.slideTo(0, 0);
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
      if (fileInput instanceof HTMLInputElement) {
        fileInput.disabled = false;
      }
      if (uploadSubmit instanceof HTMLButtonElement) {
        uploadSubmit.disabled = false;
      }
      if (uploadSpinner instanceof HTMLElement) {
        uploadSpinner.classList.add('hidden');
      }
      if (uploadText instanceof HTMLElement) {
        uploadText.textContent = 'Загрузить';
      }
    }
  });

  if (!list) return;
  list.addEventListener('click', async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const item = target.closest('[data-photo-id]');
    if (!item) return;
    const photoId = item.getAttribute('data-photo-id');
    if (!photoId) return;

    const csrfToken = getCookie('csrftoken');
    if (target.classList.contains('city-photo-delete')) {
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
        window.location.reload();
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Не удалось удалить фото';
        showError(message);
      }
    }

    if (target.classList.contains('city-photo-set-default')) {
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
        window.location.reload();
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Не удалось выбрать фото по умолчанию';
        showError(message);
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
