/**
 * Галерея изображений для контента статей и новостей.
 * При клике на изображение открывается лайтбокс GLightbox для просмотра в полном размере.
 */
import GLightbox from 'glightbox';
import 'glightbox/dist/css/glightbox.min.css';
import '../../css/content_image_gallery.css';

function initContentImageGallery() {
  const containers = document.querySelectorAll('.content-with-image-gallery');
  if (containers.length === 0) return;

  let galleryIndex = 0;
  containers.forEach((container) => {
    const images = container.querySelectorAll('img[src]');
    if (images.length === 0) return;

    const galleryId = `content-gallery-${galleryIndex++}`;
    images.forEach((img) => {
      const href = img.src || img.getAttribute('src');
      if (!href) return;

      const anchor = document.createElement('a');
      anchor.href = href;
      anchor.className = 'glightbox-content';
      anchor.setAttribute('data-gallery', galleryId);
      img.parentNode.insertBefore(anchor, img);
      anchor.appendChild(img);
    });
  });

  GLightbox({
    selector: '.content-with-image-gallery .glightbox-content',
    touchNavigation: true,
    loop: true,
    autoplayVideos: false,
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initContentImageGallery);
} else {
  initContentImageGallery();
}
