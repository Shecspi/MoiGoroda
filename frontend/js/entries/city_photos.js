import GLightbox from 'glightbox';
import 'glightbox/dist/css/glightbox.min.css';
import { getCookie } from '../components/get_cookie';

function initCityGallery() {
  const galleryLinks = document.querySelectorAll('.city-glightbox');
  if (galleryLinks.length === 0) return;

  GLightbox({
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
  const list = document.getElementById('city-photo-list');
  if (!uploadForm || !list) return;
  const carouselRoot = document.querySelector('.city-image-carousel');
  const setDefaultButton = document.getElementById('city-photo-set-default-btn');
  const defaultLabel = document.getElementById('city-photo-default-label');
  const viewport = carouselRoot?.querySelector('.hs-carousel') || null;
  const body = carouselRoot?.querySelector('.hs-carousel-body') || null;
  const slides = carouselRoot
    ? [...carouselRoot.querySelectorAll('.hs-carousel-slide[data-photo-id]')]
    : [];

  const getTranslateX = (transformValue) => {
    if (!transformValue || transformValue === 'none') return 0;
    if (transformValue.startsWith('matrix3d(')) {
      const values = transformValue.slice(9, -1).split(',').map((v) => Number(v.trim()));
      return Number.isFinite(values[12]) ? values[12] : 0;
    }
    if (transformValue.startsWith('matrix(')) {
      const values = transformValue.slice(7, -1).split(',').map((v) => Number(v.trim()));
      return Number.isFinite(values[4]) ? values[4] : 0;
    }
    return 0;
  };

  const getActiveSlide = () => {
    if (!viewport || !body || slides.length === 0) return null;

    const computedTransform = window.getComputedStyle(body).transform;
    const translateX = getTranslateX(computedTransform);
    const viewportWidth = viewport.getBoundingClientRect().width || 1;
    const rawIndex = Math.round(Math.abs(translateX) / viewportWidth);
    const index = Math.max(0, Math.min(slides.length - 1, rawIndex));
    return slides[index];
  };

  const syncControlsWithActiveSlide = () => {
    const activeSlide = getActiveSlide();
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
  if (carouselRoot) {
    const prevButton = carouselRoot.querySelector('.hs-carousel-prev');
    const nextButton = carouselRoot.querySelector('.hs-carousel-next');
    if (prevButton instanceof HTMLElement) {
      prevButton.addEventListener('click', () => {
        window.setTimeout(syncControlsWithActiveSlide, 50);
      });
    }
    if (nextButton instanceof HTMLElement) {
      nextButton.addEventListener('click', () => {
        window.setTimeout(syncControlsWithActiveSlide, 50);
      });
    }

    if (body instanceof HTMLElement) {
      const observer = new MutationObserver(() => {
        window.setTimeout(syncControlsWithActiveSlide, 0);
      });
      observer.observe(body, { attributes: true, attributeFilter: ['style', 'class'] });
      body.addEventListener('transitionend', syncControlsWithActiveSlide);
    }
  }

  uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(uploadForm);
    const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');

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
      window.location.reload();
    } catch (error) {
      showError(error.message);
    }
  });

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
        showError(error.message);
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
        showError(error.message);
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
