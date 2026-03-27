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
