import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  createMockTinyMCEEditor,
  createFileList,
  createMockFile,
} from '../test/tinymce-helpers.js';

describe('tinymce_blog_carousel_multiselect', () => {
  /** @type {ReturnType<typeof createMockTinyMCEEditor>} */
  let editor;
  let blogCarouselButton;
  let blogCarouselEditButton;
  let contextToolbarConfig;

  beforeEach(async () => {
    vi.resetModules();
    vi.useFakeTimers();
    document.body.innerHTML = '';
    delete window.djangoTinyMCESetupBlogCarousel;
    window.djangoTinyMCEUploadImageFile = vi.fn();

    await import('@static/tinymce/js/tinymce_blog_carousel_multiselect.js');

    editor = createMockTinyMCEEditor('');
    window.djangoTinyMCESetupBlogCarousel(editor);

    const addButton = editor.ui.registry.addButton;
    blogCarouselButton = addButton.mock.calls.find((c) => c[0] === 'blog_carousel')?.[1];
    blogCarouselEditButton = addButton.mock.calls.find((c) => c[0] === 'blog_carousel_edit')?.[1];
    contextToolbarConfig = editor.ui.registry.addContextToolbar.mock.calls[0]?.[1];
  });

  afterEach(() => {
    vi.useRealTimers();
    delete window.djangoTinyMCESetupBlogCarousel;
    delete window.djangoTinyMCEUploadImageFile;
  });

  function openNewCarouselDialog() {
    blogCarouselButton.onAction();
    return editor._test.getLastDialogConfig();
  }

  function getDialogPanels(dialogConfig) {
    return dialogConfig.body.items.filter((item) => item.type === 'htmlpanel');
  }

  function initDropzonePanel(dialogConfig) {
    const dropzonePanel = getDialogPanels(dialogConfig).find((p) =>
      p.html.includes('data-mg-carousel-dropzone'),
    );
    const panelEl = document.createElement('div');
    panelEl.innerHTML = dropzonePanel.html;
    document.body.appendChild(panelEl);
    dropzonePanel.onInit(panelEl);
    return panelEl;
  }

  function initExistingSlidesPanel(dialogConfig, urls) {
    const existingPanel = getDialogPanels(dialogConfig).find((p) =>
      p.html.includes('data-mg-existing-slides'),
    );
    if (!existingPanel) return null;
    const panelEl = document.createElement('div');
    panelEl.innerHTML = existingPanel.html;
    document.body.appendChild(panelEl);
    existingPanel.onInit(panelEl);
    return panelEl;
  }

  function submitDialog(dialogConfig, apiOverrides = {}) {
    const api = {
      getData: () => ({ alt: '' }),
      block: vi.fn(),
      unblock: vi.fn(),
      close: vi.fn(),
      ...apiOverrides,
    };
    dialogConfig.onSubmit(api);
    return api;
  }

  it('регистрирует кнопки и контекстный тулбар', () => {
    expect(typeof window.djangoTinyMCESetupBlogCarousel).toBe('function');
    expect(blogCarouselButton).toBeDefined();
    expect(blogCarouselEditButton).toBeDefined();
    expect(contextToolbarConfig.items).toBe('blog_carousel_edit');
  });

  it('вставляет карусель с экранированием alt и URL', async () => {
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const input = panel.querySelector('[data-mg-carousel-input]');

    const files = createFileList([
      createMockFile('a.jpg', 10, 1),
      createMockFile('b.jpg', 10, 2),
    ]);
    Object.defineProperty(input, 'files', { value: files, configurable: true });
    input.dispatchEvent(new Event('change'));

    window.djangoTinyMCEUploadImageFile.mockImplementation(() =>
      Promise.resolve('/media/"unsafe>.jpg'),
    );

    const api = submitDialog(dialog, {
      getData: () => ({ alt: 'Подпись <script>' }),
    });

    await vi.waitFor(() => {
      expect(api.close).toHaveBeenCalled();
    });

    const html = editor.insertContent.mock.calls[0][0];
    expect(html).toContain('class="mg-blog-carousel"');
    expect(html).toContain('data-mg-caption="Подпись &lt;script>"');
    expect(html).toContain('src="/media/&quot;unsafe>.jpg"');
    expect(html).toContain('width="200"');
    expect((html.match(/<img/g) || []).length).toBe(2);
  });

  it('принимает файлы, перетащенные в dropzone', async () => {
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const dropzone = panel.querySelector('[data-mg-carousel-dropzone]');

    const files = createFileList([
      createMockFile('drop-a.jpg', 10, 1),
      createMockFile('drop-b.jpg', 10, 2),
    ]);
    dropzone.dispatchEvent(
      Object.assign(new Event('drop', { bubbles: true }), {
        dataTransfer: { files },
        preventDefault: vi.fn(),
      }),
    );

    window.djangoTinyMCEUploadImageFile.mockResolvedValue('/media/drop.jpg');
    const api = submitDialog(dialog);
    await vi.waitFor(() => expect(api.close).toHaveBeenCalled());
    expect(editor.insertContent).toHaveBeenCalled();
  });

  it('требует минимум 2 изображения', () => {
    const dialog = openNewCarouselDialog();
    initDropzonePanel(dialog);
    submitDialog(dialog);
    expect(editor.windowManager.alert).toHaveBeenCalledWith(
      'В карусели должно быть минимум 2 изображения.',
    );
    expect(editor.insertContent).not.toHaveBeenCalled();
  });

  it('предупреждает при превышении лимита новых файлов', async () => {
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const input = panel.querySelector('[data-mg-carousel-input]');

    const many = Array.from({ length: 12 }, (_, i) =>
      createMockFile(`f${i}.jpg`, 10, i + 1),
    );
    Object.defineProperty(input, 'files', { value: createFileList(many), configurable: true });
    input.dispatchEvent(new Event('change'));

    window.djangoTinyMCEUploadImageFile.mockResolvedValue('/media/x.jpg');

    submitDialog(dialog);
    await vi.waitFor(() => {
      expect(editor.windowManager.alert).toHaveBeenCalledWith(
        expect.stringContaining('больше 10 новых файлов'),
      );
    });
  });

  it('дедуплицирует одинаковые файлы при повторном выборе', async () => {
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const input = panel.querySelector('[data-mg-carousel-input]');
    const fileA = createMockFile('dup.jpg', 50, 99);
    const fileB = createMockFile('other.jpg', 50, 100);

    Object.defineProperty(input, 'files', {
      value: createFileList([fileA, fileB]),
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));

    Object.defineProperty(input, 'files', {
      value: createFileList([fileA]),
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));

    window.djangoTinyMCEUploadImageFile
      .mockResolvedValueOnce('/media/1.jpg')
      .mockResolvedValueOnce('/media/2.jpg');

    const api = submitDialog(dialog);
    await vi.waitFor(() => expect(api.close).toHaveBeenCalled());

    expect(window.djangoTinyMCEUploadImageFile).toHaveBeenCalledTimes(2);
  });

  it('загружает файлы с ограниченной параллельностью и сохраняет порядок', async () => {
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const input = panel.querySelector('[data-mg-carousel-input]');

    const files = createFileList([
      createMockFile('1.jpg', 10, 1),
      createMockFile('2.jpg', 10, 2),
      createMockFile('3.jpg', 10, 3),
      createMockFile('4.jpg', 10, 4),
    ]);
    Object.defineProperty(input, 'files', { value: files, configurable: true });
    input.dispatchEvent(new Event('change'));

    let active = 0;
    let maxActive = 0;
    const order = [];

    window.djangoTinyMCEUploadImageFile.mockImplementation((file) => {
      active += 1;
      maxActive = Math.max(maxActive, active);
      return new Promise((resolve) => {
        setTimeout(() => {
          order.push(file.name);
          active -= 1;
          resolve(`/media/${file.name}`);
        }, 10);
      });
    });

    const api = submitDialog(dialog);
    await vi.runAllTimersAsync();
    await vi.waitFor(() => expect(api.close).toHaveBeenCalled());

    expect(maxActive).toBeLessThanOrEqual(3);
    expect(order).toEqual(['1.jpg', '2.jpg', '3.jpg', '4.jpg']);

    const html = editor.insertContent.mock.calls[0][0];
    expect(html.indexOf('/media/1.jpg')).toBeLessThan(html.indexOf('/media/4.jpg'));
  });

  it('не сохраняет карусель, если после удаления осталось меньше 2 фото', () => {
    editor._test.body.innerHTML = `
      <div class="mg-blog-carousel" data-mg-caption="Старая">
        <img src="/media/a.jpg" alt="Старая">
        <img src="/media/b.jpg" alt="Старая">
      </div>
    `;
    editor.selection.getNode = () => editor._test.body.querySelector('.mg-blog-carousel');

    blogCarouselEditButton.onAction();
    const dialog = editor._test.getLastDialogConfig();
    const existingPanel = initExistingSlidesPanel(dialog);

    existingPanel.querySelector('[data-mg-remove-slide]').click();

    const api = submitDialog(dialog, { getData: () => ({ alt: 'Новая' }) });
    expect(editor.windowManager.alert).toHaveBeenCalledWith(
      'В карусели должно быть минимум 2 изображения.',
    );
    expect(api.close).not.toHaveBeenCalled();
  });

  it('сохраняет карусель при редактировании с удалением и новыми файлами', async () => {
    editor._test.body.innerHTML = `
      <div class="mg-blog-carousel" data-mg-caption="Cap">
        <img src="/media/old1.jpg">
        <img src="/media/old2.jpg">
        <img src="/media/old3.jpg">
      </div>
    `;
    const carousel = editor._test.body.querySelector('.mg-blog-carousel');
    editor.selection.getNode = () => carousel;

    blogCarouselEditButton.onAction();
    const dialog = editor._test.getLastDialogConfig();
    const existingPanel = initExistingSlidesPanel(dialog);
    existingPanel.querySelector('[data-mg-remove-slide]').click();

    const dropzone = initDropzonePanel(dialog);
    const input = dropzone.querySelector('[data-mg-carousel-input]');
    Object.defineProperty(input, 'files', {
      value: createFileList([createMockFile('n1.jpg'), createMockFile('n2.jpg')]),
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));

    window.djangoTinyMCEUploadImageFile
      .mockResolvedValueOnce('/media/n1.jpg')
      .mockResolvedValueOnce('/media/n2.jpg');

    submitDialog(dialog, { getData: () => ({ alt: 'Cap' }) });
    await vi.waitFor(() => {
      expect(editor.dom.setOuterHTML).toHaveBeenCalled();
    });

    const html = editor.dom.setOuterHTML.mock.calls[0][1];
    expect(html).toContain('/media/old2.jpg');
    expect(html).toContain('/media/old3.jpg');
    expect(html).toContain('/media/n1.jpg');
    expect(html).not.toContain('/media/old1.jpg');
  });

  it('показывает ошибку при сбое загрузки', async () => {
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const input = panel.querySelector('[data-mg-carousel-input]');
    Object.defineProperty(input, 'files', {
      value: createFileList([createMockFile('a.jpg'), createMockFile('b.jpg')]),
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));

    window.djangoTinyMCEUploadImageFile.mockRejectedValue(new Error('Сеть недоступна'));

    const api = submitDialog(dialog);
    await vi.waitFor(() => {
      expect(editor.windowManager.alert).toHaveBeenCalledWith('Сеть недоступна');
    });
    expect(api.unblock).toHaveBeenCalled();
    expect(api.close).not.toHaveBeenCalled();
  });

  it('отклоняет загрузку, если djangoTinyMCEUploadImageFile недоступен', async () => {
    delete window.djangoTinyMCEUploadImageFile;
    const dialog = openNewCarouselDialog();
    const panel = initDropzonePanel(dialog);
    const input = panel.querySelector('[data-mg-carousel-input]');
    Object.defineProperty(input, 'files', {
      value: createFileList([createMockFile('a.jpg'), createMockFile('b.jpg')]),
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));

    const api = submitDialog(dialog);
    await vi.waitFor(() => {
      expect(editor.windowManager.alert).toHaveBeenCalledWith(
        'Загрузка изображений недоступна',
      );
    });
    expect(api.unblock).toHaveBeenCalled();
  });

  it('открывает редактирование по двойному клику', () => {
    editor._test.body.innerHTML = `
      <div class="mg-blog-carousel">
        <img src="/media/a.jpg"><img src="/media/b.jpg">
      </div>
    `;
    const img = editor._test.body.querySelector('img');
    const handlers = editor._test.onHandlers.get('dblclick') || [];
    const evt = { target: img, preventDefault: vi.fn() };
    handlers[0](evt);

    expect(evt.preventDefault).toHaveBeenCalled();
    expect(editor._test.getLastDialogConfig().title).toBe('Изменить карусель');
  });

  it('контекстный тулбар активен только на карусели', () => {
    const carousel = document.createElement('div');
    carousel.className = 'mg-blog-carousel';
    expect(contextToolbarConfig.predicate(carousel)).toBe(true);
    expect(contextToolbarConfig.predicate(document.createElement('p'))).toBe(false);
  });

  it('парсит alt из data-mg-caption при редактировании', () => {
    editor._test.body.innerHTML = `
      <div class="mg-blog-carousel" data-mg-caption="Из блока">
        <img src="/media/a.jpg"><img src="/media/b.jpg">
      </div>
    `;
    editor.selection.getNode = () => editor._test.body.querySelector('.mg-blog-carousel');
    blogCarouselEditButton.onAction();
    const dialog = editor._test.getLastDialogConfig();
    expect(dialog.initialData.alt).toBe('Из блока');
  });

  it('повторно привязывает dropzone в onOpen через setTimeout', async () => {
    const dialog = openNewCarouselDialog();
    const dropzonePanel = getDialogPanels(dialog).find((p) =>
      p.html.includes('data-mg-carousel-dropzone'),
    );
    const panelEl = document.createElement('div');
    panelEl.innerHTML = dropzonePanel.html;
    document.body.appendChild(panelEl);

    dialog.onOpen();
    vi.runAllTimers();
    dropzonePanel.onInit(panelEl);

    const input = panelEl.querySelector('[data-mg-carousel-input]');
    Object.defineProperty(input, 'files', {
      value: createFileList([createMockFile('a.jpg'), createMockFile('b.jpg')]),
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));

    window.djangoTinyMCEUploadImageFile.mockResolvedValue('/media/x.jpg');
    const api = submitDialog(dialog);
    await vi.waitFor(() => expect(api.close).toHaveBeenCalled());
  });
});
