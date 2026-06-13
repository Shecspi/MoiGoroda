import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createMockTinyMCEEditor } from '../test/tinymce-helpers.js';

describe('tinymce_content_image', () => {
  beforeEach(async () => {
    vi.resetModules();
    vi.useFakeTimers();
    delete window.djangoTinyMCESetupContentImage;
    delete window.djangoTinyMCEImagesUploadHandler;
    await import('@static/tinymce/js/tinymce_content_image.js');
  });

  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = '';
    delete window.djangoTinyMCESetupContentImage;
    delete window.djangoTinyMCEImagesUploadHandler;
  });

  function setupEditor(html = '') {
    const editor = createMockTinyMCEEditor(html);
    window.djangoTinyMCESetupContentImage(editor);
    return editor;
  }

  it('регистрирует setup на window', () => {
    expect(typeof window.djangoTinyMCESetupContentImage).toBe('function');
  });

  it('не ресайзит изображения внутри карусели', () => {
    const editor = setupEditor(`
      <div class="mg-blog-carousel">
        <img src="/media/c.jpg" width="999">
      </div>
    `);
    vi.runAllTimers();

    const img = editor.getBody().querySelector('img');
    expect(img.getAttribute('width')).toBe('999');
    expect(img.getAttribute('data-mg-content-sized')).toBeNull();
  });

  it('устанавливает 200px по высоте для вертикального одиночного фото', () => {
    const editor = setupEditor('<img src="/media/tall.jpg">');
    const img = editor.getBody().querySelector('img');
    Object.defineProperty(img, 'naturalWidth', { value: 400, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 800, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    editor.trigger('init');
    vi.runAllTimers();

    expect(img.getAttribute('height')).toBe('200');
    expect(img.getAttribute('data-mg-content-sized')).toBe('true');
    expect(img.getAttribute('style')).toContain('height: 200px');
  });

  it('устанавливает 200px по ширине для горизонтального одиночного фото', () => {
    const editor = setupEditor('<img src="/media/wide.jpg">');
    const img = editor.getBody().querySelector('img');
    Object.defineProperty(img, 'naturalWidth', { value: 1200, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 600, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    editor.trigger('init');
    vi.runAllTimers();

    expect(img.getAttribute('width')).toBe('200');
    expect(img.getAttribute('data-mg-content-sized')).toBe('true');
  });

  it('оборачивает одиночное изображение в параграф и убирает float', () => {
    const editor = setupEditor(
      '<img src="/media/f.jpg" class="alignleft" style="float:left;margin-left:10px">',
    );
    const img = editor.getBody().querySelector('img');
    Object.defineProperty(img, 'naturalWidth', { value: 800, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 600, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    editor.trigger('init');
    vi.runAllTimers();

    const parent = img.parentElement;
    expect(parent?.nodeName).toBe('P');
    expect(img.style.float).toBe('');
    expect(img.className).not.toContain('alignleft');
  });

  it('разделяет несколько img в одном блоке на отдельные параграфы', () => {
    const editor = setupEditor(`
      <p>
        <img src="/media/1.jpg">
        <img src="/media/2.jpg">
      </p>
    `);
    const imgs = editor.getBody().querySelectorAll('img');
    imgs.forEach((img) => {
      Object.defineProperty(img, 'naturalWidth', { value: 800, configurable: true });
      Object.defineProperty(img, 'naturalHeight', { value: 600, configurable: true });
      Object.defineProperty(img, 'complete', { value: true, configurable: true });
    });

    editor.trigger('init');
    vi.runAllTimers();

    const paragraphs = editor.getBody().querySelectorAll('p');
    expect(paragraphs.length).toBeGreaterThanOrEqual(2);
    paragraphs.forEach((p) => {
      expect(p.querySelectorAll('img').length).toBeLessThanOrEqual(1);
    });
  });

  it('синхронизирует data-mg-caption на обёртке по alt', () => {
    const editor = setupEditor('<p><img src="/media/cap.jpg" alt="Закат"></p>');
    const img = editor.getBody().querySelector('img');
    Object.defineProperty(img, 'naturalWidth', { value: 800, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 600, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    editor.trigger('init');
    vi.runAllTimers();

    const wrapper = img.parentElement;
    expect(wrapper?.getAttribute('data-mg-caption')).toBe('Закат');
    expect(img.getAttribute('data-mg-caption')).toBeNull();
  });

  it('удаляет data-mg-caption у одиночных блоков при PostProcess', () => {
    const editor = setupEditor('');
    const payload = {
      get: true,
      content:
        '<p data-mg-caption="Тест"><img src="/x.jpg" alt="Тест"></p>' +
        '<div class="mg-blog-carousel" data-mg-caption="Карусель"><img src="/y.jpg"></div>',
    };
    editor.trigger('PostProcess', payload);

    expect(payload.content).toContain('mg-blog-carousel');
    expect(payload.content).toContain('data-mg-caption="Карусель"');
    expect(payload.content).not.toMatch(/<p[^>]*data-mg-caption/);
  });

  it('оборачивает загрузчик изображений и планирует ресайз', async () => {
    const originalHandler = vi.fn().mockResolvedValue('/media/new.jpg');
    window.djangoTinyMCEImagesUploadHandler = originalHandler;

    const editor = setupEditor('<img src="/media/new.jpg">');
    const img = editor.getBody().querySelector('img');
    Object.defineProperty(img, 'naturalWidth', { value: 1000, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 500, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    const blobInfo = {
      blob: () => new File(['x'], 'u.jpg', { type: 'image/jpeg' }),
      filename: () => 'u.jpg',
      width: () => 1000,
      height: () => 500,
    };

    const handler = editor.options.set.mock.calls.find(
      (c) => c[0] === 'images_upload_handler',
    )?.[1];
    expect(handler).toBeTypeOf('function');

    await handler(blobInfo, vi.fn());
    vi.advanceTimersByTime(100);

    expect(originalHandler).toHaveBeenCalled();
    expect(img.getAttribute('data-mg-content-sized')).toBe('true');
  });

  it('плановый scan ресайзит изображение после Change', () => {
    const editor = setupEditor('<img src="/media/obs.jpg">');
    const img = editor.getBody().querySelector('img');
    Object.defineProperty(img, 'naturalWidth', { value: 400, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 900, configurable: true });
    Object.defineProperty(img, 'complete', { value: true, configurable: true });

    editor.trigger('Change');
    vi.runAllTimers();

    expect(img.getAttribute('data-mg-content-sized')).toBe('true');
    expect(img.getAttribute('height')).toBe('200');
  });

  it('помечает img как sized после ObjectResized', () => {
    const editor = setupEditor('<img src="/media/r.jpg">');
    const img = editor.getBody().querySelector('img');
    editor.trigger('ObjectResized', { target: img });
    expect(img.getAttribute('data-mg-content-sized')).toBe('true');
  });
});
