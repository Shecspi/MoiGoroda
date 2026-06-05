import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const initBlogContentCarousels = vi.fn();
const applyStandardContentImageSize = vi.fn((img) => {
  img.setAttribute('data-sized', 'true');
});
const glightboxMock = vi.fn();

vi.mock('./blog_content_carousel.js', () => ({
  initBlogContentCarousels,
  applyStandardContentImageSize,
}));

vi.mock('glightbox', () => ({
  default: glightboxMock,
}));

describe('content_image_gallery', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    document.body.innerHTML = '';
    Object.defineProperty(document, 'readyState', {
      value: 'complete',
      configurable: true,
    });
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  async function loadGalleryModule() {
    await import('./content_image_gallery.js');
  }

  it('инициализирует карусели при загрузке модуля', async () => {
    await loadGalleryModule();
    expect(initBlogContentCarousels).toHaveBeenCalled();
  });

  it('оборачивает одиночные изображения в glightbox и добавляет подпись', async () => {
    const container = document.createElement('div');
    container.className = 'content-with-image-gallery';
    container.innerHTML =
      '<p><img src="/media/photo.jpg" alt="Вид на город"></p>';
    document.body.appendChild(container);

    await loadGalleryModule();

    const anchor = container.querySelector('a.glightbox-content');
    expect(anchor).not.toBeNull();
    expect(anchor.href).toContain('/media/photo.jpg');
    expect(anchor.getAttribute('data-gallery')).toBe('content-gallery-0');
    expect(anchor.querySelector('img')).not.toBeNull();
    expect(applyStandardContentImageSize).toHaveBeenCalled();

    const caption = container.querySelector('.content-image-caption');
    expect(caption?.textContent).toBe('Вид на город');

    expect(glightboxMock).toHaveBeenCalledWith(
      expect.objectContaining({
        selector: '.content-with-image-gallery .glightbox-content',
        loop: true,
      }),
    );
  });

  it('не оборачивает изображения внутри карусели', async () => {
    const container = document.createElement('div');
    container.className = 'content-with-image-gallery';
    container.innerHTML = `
      <div class="mg-blog-carousel">
        <img src="/media/c1.jpg" alt="c1">
        <img src="/media/c2.jpg" alt="c2">
      </div>
      <p><img src="/media/alone.jpg" alt="solo"></p>
    `;
    document.body.appendChild(container);

    await loadGalleryModule();

    const carousel = container.querySelector('.mg-blog-carousel');
    expect(carousel.querySelector('a.glightbox-content')).toBeNull();

    const standaloneAnchor = container.querySelector('p a.glightbox-content');
    expect(standaloneAnchor).not.toBeNull();
    expect(standaloneAnchor.querySelector('img')?.getAttribute('src')).toContain('/media/alone.jpg');
  });

  it('не оборачивает изображения, уже внутри glightbox-content', async () => {
    const container = document.createElement('div');
    container.className = 'content-with-image-gallery';
    container.innerHTML = `
      <a class="glightbox-content" href="/media/x.jpg">
        <img src="/media/x.jpg" alt="x">
      </a>
    `;
    document.body.appendChild(container);

    await loadGalleryModule();

    expect(container.querySelectorAll('a.glightbox-content')).toHaveLength(1);
  });

  it('не вызывает GLightbox, если на странице нет контейнера галереи', async () => {
    document.body.innerHTML = '<p>Только текст</p>';
    await loadGalleryModule();
    expect(glightboxMock).not.toHaveBeenCalled();
  });

  it('инициализирует GLightbox при контейнере даже без изображений', async () => {
    const container = document.createElement('div');
    container.className = 'content-with-image-gallery';
    container.innerHTML = '<p>Только текст</p>';
    document.body.appendChild(container);

    await loadGalleryModule();

    expect(glightboxMock).toHaveBeenCalled();
  });
});
