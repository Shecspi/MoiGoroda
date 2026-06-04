/**
 * Карусель фотографий в контенте статей блога (блок .mg-blog-carousel из TinyMCE).
 * Визуально совпадает с одиночными изображениями: 500px по ширине или высоте, тень, подпись.
 */
import Swiper from 'swiper';
import { Navigation, Thumbs, FreeMode } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/free-mode';

const CAROUSEL_SELECTOR = '.mg-blog-carousel';
const MIN_SLIDES = 2;
const CONTENT_IMAGE_SIZE = 500;

const NAV_BTN_BASE = 'swiper-button mg-blog-carousel-nav content-gallery-lightbox-nav';
/** Те же SVG, что у GLightbox (glightbox-clean .gprev / .gnext). */
const GLIGHTBOX_PREV_ICON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 477.175 477.175" aria-hidden="true"><path d="M145.188,238.575l215.5-215.5c5.3-5.3,5.3-13.8,0-19.1s-13.8-5.3-19.1,0l-225.1,225.1c-5.3,5.3-5.3,13.8,0,19.1l225.1,225c2.6,2.6,6.1,4,9.5,4s6.9-1.3,9.5-4c5.3-5.3,5.3-13.8,0-19.1L145.188,238.575z"/></svg>';
const GLIGHTBOX_NEXT_ICON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 477.175 477.175" aria-hidden="true"><path d="M360.731,229.075l-225.1-225.1c-5.3-5.3-13.8-5.3-19.1,0s-5.3,13.8,0,19.1l215.5,215.5l-215.5,215.5c-5.3,5.3-5.3,13.8,0,19.1c2.6,2.6,6.1,4,9.5,4c3.4,0,6.9-1.3,9.5-4l225.1-225.1C365.931,242.875,365.931,234.275,360.731,229.075z"/></svg>';

const THUMB_SLIDE_CLASS =
  'swiper-slide mg-blog-carousel-thumb block p-0 appearance-none relative !w-20 !h-14 rounded-md overflow-hidden border border-gray-200 dark:border-neutral-700 bg-gray-100 dark:bg-neutral-800 cursor-pointer opacity-50 transition-opacity duration-200 ease-out [&.swiper-slide-thumb-active]:opacity-100';

/** Как в редакторе: горизонтальные — width 500, вертикальные — height 500. */
export function applyStandardContentImageSize(img) {
  const apply = () => {
    const w = img.naturalWidth;
    const h = img.naturalHeight;
    if (!w || !h) return;

    if (h > w) {
      img.removeAttribute('width');
      img.setAttribute('height', String(CONTENT_IMAGE_SIZE));
    } else {
      img.removeAttribute('height');
      img.setAttribute('width', String(CONTENT_IMAGE_SIZE));
    }
  };

  if (img.complete && img.naturalWidth) {
    apply();
  } else {
    img.addEventListener('load', apply, { once: true });
  }
}

function collectImages(carouselEl) {
  return [...carouselEl.querySelectorAll('img[src]')].filter((img) => {
    const src = img.src || img.getAttribute('src');
    return Boolean(src);
  });
}

function cloneContentImage(sourceImg) {
  const slideImg = sourceImg.cloneNode(true);
  slideImg.removeAttribute('class');
  slideImg.removeAttribute('style');
  slideImg.loading = 'lazy';
  slideImg.decoding = 'async';

  if (!slideImg.hasAttribute('width') && !slideImg.hasAttribute('height')) {
    slideImg.setAttribute('width', String(CONTENT_IMAGE_SIZE));
  }
  applyStandardContentImageSize(slideImg);

  return slideImg;
}

function buildSlide(sourceImg, galleryId, slideIndex, totalSlides, carouselIndex) {
  const href = sourceImg.src || sourceImg.getAttribute('src');
  const slide = document.createElement('div');
  slide.className = 'swiper-slide mg-blog-carousel-slide shrink-0 w-full';
  slide.setAttribute('role', 'group');
  slide.setAttribute('aria-roledescription', 'slide');
  slide.setAttribute('aria-label', `Слайд ${slideIndex + 1} из ${totalSlides}`);

  const slideBlock = document.createElement('div');
  slideBlock.className = 'mg-blog-carousel-slide-inner';

  const anchor = document.createElement('a');
  anchor.href = href;
  anchor.className = 'glightbox-content block w-full';
  anchor.setAttribute('data-gallery', galleryId);
  anchor.setAttribute('data-type', 'image');

  const slideImg = cloneContentImage(sourceImg);
  slideImg.classList.add('mg-blog-carousel-main-img');
  anchor.appendChild(slideImg);
  slideBlock.appendChild(anchor);

  const alt = sourceImg.alt || slideImg.alt || '';
  if (alt) {
    const captionId = `mg-blog-carousel-caption-${carouselIndex}-${slideIndex}`;
    const caption = document.createElement('figcaption');
    caption.id = captionId;
    caption.className = 'content-image-caption';
    caption.textContent = alt;
    anchor.setAttribute('aria-describedby', captionId);
    slideImg.setAttribute('aria-describedby', captionId);
    slideBlock.appendChild(caption);
  }

  slide.appendChild(slideBlock);
  return slide;
}

function buildThumbSlide(sourceImg, slideIndex, totalSlides) {
  const src = sourceImg.src || sourceImg.getAttribute('src');
  const alt = sourceImg.alt || `Миниатюра ${slideIndex + 1}`;

  const thumb = document.createElement('button');
  thumb.type = 'button';
  thumb.className = THUMB_SLIDE_CLASS;
  thumb.setAttribute('role', 'tab');
  thumb.setAttribute('aria-label', `Показать фото ${slideIndex + 1} из ${totalSlides}`);
  thumb.setAttribute('aria-selected', slideIndex === 0 ? 'true' : 'false');

  const thumbImg = document.createElement('img');
  thumbImg.src = src;
  thumbImg.alt = alt;
  thumbImg.loading = 'lazy';
  thumbImg.decoding = 'async';
  thumbImg.className = 'mg-blog-carousel-thumb-img h-full w-full object-cover';
  thumb.appendChild(thumbImg);

  return thumb;
}

function syncThumbAriaSelected(thumbsSwiper, activeIndex) {
  thumbsSwiper?.slides?.forEach((slide, index) => {
    const tab = slide.querySelector('.mg-blog-carousel-thumb');
    if (tab) {
      tab.setAttribute('aria-selected', index === activeIndex ? 'true' : 'false');
    }
  });
}

function announceSlide(swiper, liveRegion, totalSlides) {
  if (!liveRegion || totalSlides <= 0) return;
  const index = swiper.activeIndex + 1;
  liveRegion.textContent = `Фото ${index} из ${totalSlides}`;
}

function bindCarouselFocusTrap(widget) {
  widget.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;

    const focusables = [
      ...widget.querySelectorAll(
        'button:not([disabled]), a[href], .mg-blog-carousel-thumb'
      ),
    ].filter((el) => el.offsetParent !== null);

    if (focusables.length === 0) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
}

function initBlogCarousel(carouselEl, index) {
  const images = collectImages(carouselEl);
  if (images.length < MIN_SLIDES) return;

  const galleryId = `blog-carousel-${index}`;
  const totalSlides = images.length;
  const swiperId = `mg-blog-carousel-swiper-${index}`;
  const thumbsId = `mg-blog-carousel-thumbs-${index}`;

  carouselEl.setAttribute('role', 'region');
  carouselEl.setAttribute('aria-roledescription', 'карусель');
  carouselEl.setAttribute('aria-label', 'Галерея фотографий');

  const widget = document.createElement('div');
  widget.className = 'mg-blog-carousel-widget relative mx-auto w-full max-w-[500px]';
  widget.setAttribute('tabindex', '0');
  widget.setAttribute('aria-label', 'Управление каруселью');

  const liveRegion = document.createElement('div');
  liveRegion.className = 'mg-blog-carousel-live';
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  widget.appendChild(liveRegion);

  const carouselMain = document.createElement('div');
  carouselMain.className = 'mg-blog-carousel-main relative';

  const swiperRoot = document.createElement('div');
  swiperRoot.id = swiperId;
  swiperRoot.className = 'swiper mg-blog-carousel-swiper w-full overflow-hidden';
  swiperRoot.setAttribute('aria-roledescription', 'carousel');
  swiperRoot.setAttribute('aria-label', 'Слайды');

  const wrapper = document.createElement('div');
  wrapper.className = 'swiper-wrapper';
  images.forEach((img, slideIndex) => {
    wrapper.appendChild(buildSlide(img, galleryId, slideIndex, totalSlides, index));
  });
  swiperRoot.appendChild(wrapper);
  carouselMain.appendChild(swiperRoot);

  const prevButton = document.createElement('button');
  prevButton.type = 'button';
  prevButton.className = `${NAV_BTN_BASE} swiper-button-prev mg-blog-carousel-prev`;
  prevButton.setAttribute('aria-label', 'Предыдущее фото');
  prevButton.setAttribute('aria-controls', swiperId);
  prevButton.innerHTML = GLIGHTBOX_PREV_ICON;

  const nextButton = document.createElement('button');
  nextButton.type = 'button';
  nextButton.className = `${NAV_BTN_BASE} swiper-button-next mg-blog-carousel-next`;
  nextButton.setAttribute('aria-label', 'Следующее фото');
  nextButton.setAttribute('aria-controls', swiperId);
  nextButton.innerHTML = GLIGHTBOX_NEXT_ICON;

  carouselMain.appendChild(prevButton);
  carouselMain.appendChild(nextButton);
  widget.appendChild(carouselMain);

  const thumbsPanel = document.createElement('div');
  thumbsPanel.className = 'mg-blog-carousel-thumbs-panel';
  thumbsPanel.setAttribute('role', 'tablist');
  thumbsPanel.setAttribute('aria-label', 'Миниатюры фотографий');

  const thumbsRoot = document.createElement('div');
  thumbsRoot.id = thumbsId;
  thumbsRoot.className = 'swiper mg-blog-carousel-thumbs';

  const thumbsWrapper = document.createElement('div');
  thumbsWrapper.className = 'swiper-wrapper';
  images.forEach((img, slideIndex) => {
    thumbsWrapper.appendChild(buildThumbSlide(img, slideIndex, totalSlides));
  });
  thumbsRoot.appendChild(thumbsWrapper);
  thumbsPanel.appendChild(thumbsRoot);
  widget.appendChild(thumbsPanel);

  carouselEl.replaceChildren(widget);
  carouselEl.classList.add('mg-blog-carousel--initialized');
  carouselEl.dataset.mgBlogCarouselReady = 'true';

  const thumbsSwiper = new Swiper(thumbsRoot, {
    modules: [FreeMode],
    spaceBetween: 8,
    slidesPerView: 'auto',
    centerInsufficientSlides: true,
    freeMode: true,
    watchSlidesProgress: true,
  });

  const swiper = new Swiper(swiperRoot, {
    modules: [Navigation, Thumbs],
    slidesPerView: 1,
    spaceBetween: 0,
    speed: 300,
    autoHeight: true,
    watchOverflow: true,
    navigation: {
      prevEl: prevButton,
      nextEl: nextButton,
    },
    thumbs: {
      swiper: thumbsSwiper,
      multipleActiveThumbs: false,
    },
    keyboard: {
      enabled: true,
      onlyInViewport: true,
    },
  });

  const onSlideChange = () => {
    announceSlide(swiper, liveRegion, totalSlides);
    syncThumbAriaSelected(thumbsSwiper, swiper.activeIndex);
  };

  announceSlide(swiper, liveRegion, totalSlides);
  swiper.on('slideChange', onSlideChange);

  swiperRoot.querySelectorAll('img').forEach((img) => {
    const bump = () => swiper.updateAutoHeight(swiper.params.speed ?? 300);
    if (img.complete) {
      bump();
    } else {
      img.addEventListener('load', bump, { once: true });
    }
  });

  bindCarouselFocusTrap(widget);
}

export function initBlogContentCarousels(root = document) {
  const containers = root.querySelectorAll('.content-with-image-gallery');
  let carouselIndex = 0;

  containers.forEach((container) => {
    container.querySelectorAll(CAROUSEL_SELECTOR).forEach((carouselEl) => {
      if (carouselEl.dataset.mgBlogCarouselReady === 'true') return;
      initBlogCarousel(carouselEl, carouselIndex++);
    });
  });
}
