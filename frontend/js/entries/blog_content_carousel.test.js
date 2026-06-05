import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const swiperInstances = [];

vi.mock('swiper', () => ({
  default: class MockSwiper {
    constructor(rootEl, options) {
      this.rootEl = rootEl;
      this.options = options;
      this.activeIndex = 0;
      this.params = { speed: 300 };
      this.slides = [];
      this._handlers = {};
      swiperInstances.push(this);
    }

    on(event, handler) {
      this._handlers[event] = handler;
    }

    updateAutoHeight() {}

    emit(event) {
      this._handlers[event]?.();
    }
  },
}));

vi.mock('swiper/modules', () => ({
  Navigation: {},
  Thumbs: {},
  FreeMode: {},
}));

vi.mock('swiper/css', () => ({}));
vi.mock('swiper/css/navigation', () => ({}));
vi.mock('swiper/css/free-mode', () => ({}));

import {
  applyStandardContentImageSize,
  initBlogContentCarousels,
} from './blog_content_carousel.js';

function buildCarouselHtml(urls, alt = '') {
  const altAttr = alt ? ` alt="${alt}"` : '';
  const captionAttr = alt ? ` data-mg-caption="${alt}"` : '';
  const imgs = urls
    .map((url) => `<img src="${url}" width="200"${altAttr}>`)
    .join('');
  return `<div class="mg-blog-carousel" data-mg-blog-carousel${captionAttr}>${imgs}</div>`;
}

describe('applyStandardContentImageSize', () => {
  it('ставит height=500 для вертикального изображения', () => {
    const img = document.createElement('img');
    Object.defineProperty(img, 'naturalWidth', { value: 400, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 800, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    applyStandardContentImageSize(img);

    expect(img.getAttribute('height')).toBe('500');
    expect(img.hasAttribute('width')).toBe(false);
  });

  it('ставит width=500 для горизонтального изображения', () => {
    const img = document.createElement('img');
    Object.defineProperty(img, 'naturalWidth', { value: 1200, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 600, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    applyStandardContentImageSize(img);

    expect(img.getAttribute('width')).toBe('500');
    expect(img.hasAttribute('height')).toBe(false);
  });

  it('ждёт load, если naturalWidth ещё нет', () => {
    const img = document.createElement('img');
    Object.defineProperty(img, 'complete', { value: false, configurable: true });
    Object.defineProperty(img, 'naturalWidth', { value: 0, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 0, configurable: true });

    applyStandardContentImageSize(img);

    Object.defineProperty(img, 'naturalWidth', { value: 1000, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 500, configurable: true });
    img.dispatchEvent(new Event('load'));

    expect(img.getAttribute('width')).toBe('500');
  });
});

describe('initBlogContentCarousels', () => {
  let container;

  beforeEach(() => {
    swiperInstances.length = 0;
    document.body.innerHTML = '';
    container = document.createElement('div');
    container.className = 'content-with-image-gallery';
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('не инициализирует карусель с одним изображением', () => {
    container.innerHTML = buildCarouselHtml(['/media/a.jpg']);
    initBlogContentCarousels();
    expect(container.querySelector('.mg-blog-carousel-widget')).toBeNull();
    expect(swiperInstances).toHaveLength(0);
  });

  it('строит виджет Swiper и glightbox-ссылки для двух и более фото', () => {
    container.innerHTML = buildCarouselHtml(
      ['/media/a.jpg', '/media/b.jpg'],
      'Подпись',
    );
    initBlogContentCarousels();

    const carousel = container.querySelector('.mg-blog-carousel');
    expect(carousel.dataset.mgBlogCarouselReady).toBe('true');
    expect(carousel.classList.contains('mg-blog-carousel--initialized')).toBe(true);

    const widget = carousel.querySelector('.mg-blog-carousel-widget');
    expect(widget).not.toBeNull();
    expect(widget.getAttribute('tabindex')).toBe('0');

    const mainLinks = carousel.querySelectorAll('.mg-blog-carousel-main .glightbox-content');
    expect(mainLinks).toHaveLength(2);
    expect(mainLinks[0].href).toContain('/media/a.jpg');
    expect(mainLinks[0].getAttribute('data-gallery')).toBe('blog-carousel-0');

    const caption = carousel.querySelector('.content-image-caption');
    expect(caption?.textContent).toBe('Подпись');

    expect(swiperInstances).toHaveLength(2);
    const mainSwiper = swiperInstances[1];
    expect(mainSwiper.options.navigation).toBeDefined();
    expect(mainSwiper.options.thumbs).toBeDefined();
  });

  it('не переинициализирует уже готовую карусель', () => {
    container.innerHTML = buildCarouselHtml(['/media/a.jpg', '/media/b.jpg']);
    initBlogContentCarousels();
    const firstWidget = container.querySelector('.mg-blog-carousel-widget');
    swiperInstances.length = 0;

    initBlogContentCarousels();

    expect(container.querySelector('.mg-blog-carousel-widget')).toBe(firstWidget);
    expect(swiperInstances).toHaveLength(0);
  });

  it('объявляет смену слайда в live region', () => {
    container.innerHTML = buildCarouselHtml(['/media/a.jpg', '/media/b.jpg', '/media/c.jpg']);
    initBlogContentCarousels();

    const live = container.querySelector('.mg-blog-carousel-live');
    expect(live?.textContent).toMatch(/Фото 1 из 3/);

    const mainSwiper = swiperInstances[1];
    mainSwiper.activeIndex = 1;
    mainSwiper.emit('slideChange');
    expect(live?.textContent).toBe('Фото 2 из 3');
  });

  it('синхронизирует aria-selected у миниатюр', () => {
    container.innerHTML = buildCarouselHtml(['/media/a.jpg', '/media/b.jpg']);
    initBlogContentCarousels();

    const thumbs = [...container.querySelectorAll('.mg-blog-carousel-thumb')];
    expect(thumbs[0].getAttribute('aria-selected')).toBe('true');
    expect(thumbs[1].getAttribute('aria-selected')).toBe('false');

    const mainSwiper = swiperInstances[1];
    const thumbsSwiper = swiperInstances[0];
    thumbsSwiper.slides = thumbs.map((tab) => {
      const slide = document.createElement('div');
      slide.appendChild(tab);
      return slide;
    });

    mainSwiper.activeIndex = 1;
    mainSwiper.emit('slideChange');

    expect(thumbs[0].getAttribute('aria-selected')).toBe('false');
    expect(thumbs[1].getAttribute('aria-selected')).toBe('true');
  });

  it('создаёт панель миниатюр с role=tablist и aria-label', () => {
    container.innerHTML = buildCarouselHtml(['/media/a.jpg', '/media/b.jpg']);
    initBlogContentCarousels();

    const thumbsPanel = container.querySelector('.mg-blog-carousel-thumbs-panel');
    expect(thumbsPanel?.getAttribute('role')).toBe('tablist');
    expect(thumbsPanel?.getAttribute('aria-label')).toBe('Миниатюры фотографий');
    expect(container.querySelectorAll('.mg-blog-carousel-thumb[role="tab"]')).toHaveLength(2);
  });
});
