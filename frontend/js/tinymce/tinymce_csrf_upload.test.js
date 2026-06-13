import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('tinymce_csrf_upload', () => {
  /** @type {typeof import('./tinymce_csrf_upload.js')} */
  let uploadModuleLoaded;
  let cookieValue = '';

  beforeEach(async () => {
    vi.resetModules();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('fetch should be mocked per test')),
    );
    cookieValue = 'csrftoken=test-csrf-token';
    vi.spyOn(document, 'cookie', 'get').mockImplementation(() => cookieValue);
    vi.spyOn(document, 'cookie', 'set').mockImplementation((value) => {
      cookieValue = value;
    });
    await import('@static/tinymce/js/tinymce_csrf_upload.js');
    uploadModuleLoaded = true;
  });

  afterEach(() => {
    cookieValue = '';
    delete window.djangoTinyMCEUploadImageFile;
    delete window.djangoTinyMCEImagesUploadHandler;
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('экспортирует обработчики на window', () => {
    expect(uploadModuleLoaded).toBe(true);
    expect(typeof window.djangoTinyMCEUploadImageFile).toBe('function');
    expect(typeof window.djangoTinyMCEImagesUploadHandler).toBe('function');
  });

  it('отклоняет загрузку без CSRF-токена', async () => {
    cookieValue = '';
    const file = new File(['data'], 'a.jpg', { type: 'image/jpeg' });
    await expect(window.djangoTinyMCEUploadImageFile(file, 'a.jpg')).rejects.toBe(
      'CSRF token not found',
    );
    expect(fetch).not.toHaveBeenCalled();
  });

  it('загружает через fetch без onProgress', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ location: '/media/uploaded.jpg' }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const file = new File(['data'], 'pic.jpg', { type: 'image/jpeg' });
    const url = await window.djangoTinyMCEUploadImageFile(file, 'pic.jpg');

    expect(url).toBe('/media/uploaded.jpg');
    expect(fetchMock).toHaveBeenCalledWith(
      '/tinymce/upload-image/',
      expect.objectContaining({
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': 'test-csrf-token' },
      }),
    );
  });

  it('отклоняет fetch-ответ без location', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ error: 'bad file' }),
      }),
    );

    const file = new File(['data'], 'pic.jpg', { type: 'image/jpeg' });
    await expect(window.djangoTinyMCEUploadImageFile(file)).rejects.toBe(
      'No location in response',
    );
  });

  it('загружает через XHR с onProgress', async () => {
    const progressCalls = [];
    class MockXHR {
      constructor() {
        this.upload = { onprogress: null };
        this.status = 200;
        this.responseText = JSON.stringify({ location: '/media/xhr.jpg' });
        MockXHR.lastInstance = this;
      }

      open() {}

      setRequestHeader() {}

      send() {
        this.upload.onprogress?.({
          lengthComputable: true,
          loaded: 50,
          total: 100,
        });
        this.onload?.();
      }
    }
    MockXHR.lastInstance = null;
    vi.stubGlobal('XMLHttpRequest', MockXHR);

    const file = new File(['data'], 'xhr.jpg', { type: 'image/jpeg' });
    const url = await window.djangoTinyMCEUploadImageFile(file, 'xhr.jpg', {
      onProgress: (p) => progressCalls.push(p),
    });

    expect(url).toBe('/media/xhr.jpg');
    expect(progressCalls).toContain(50);
    expect(MockXHR.lastInstance.withCredentials).toBe(true);
  });

  it('отклоняет XHR при невалидном JSON', async () => {
    class MockXHR {
      constructor() {
        this.upload = { onprogress: null };
        this.status = 200;
        this.responseText = 'not json';
      }

      open() {}

      setRequestHeader() {}

      send() {
        this.onload?.();
      }
    }
    vi.stubGlobal('XMLHttpRequest', MockXHR);

    const file = new File(['data'], 'bad.jpg', { type: 'image/jpeg' });
    await expect(
      window.djangoTinyMCEUploadImageFile(file, 'bad.jpg', { onProgress: () => {} }),
    ).rejects.toBe('Upload failed: invalid response');
  });

  it('отклоняет XHR при HTTP-ошибке', async () => {
    class MockXHR {
      constructor() {
        this.upload = { onprogress: null };
        this.status = 403;
        this.responseText = '';
      }

      open() {}

      setRequestHeader() {}

      send() {
        this.onload?.();
      }
    }
    vi.stubGlobal('XMLHttpRequest', MockXHR);

    const file = new File(['data'], 'denied.jpg', { type: 'image/jpeg' });
    await expect(
      window.djangoTinyMCEUploadImageFile(file, 'denied.jpg', { onProgress: () => {} }),
    ).rejects.toBe('Upload failed: 403');
  });

  it('djangoTinyMCEImagesUploadHandler проксирует blobInfo через XHR', async () => {
    class MockXHR {
      constructor() {
        this.upload = { onprogress: null };
        this.status = 200;
        this.responseText = JSON.stringify({ location: '/media/handler.jpg' });
      }

      open() {}

      setRequestHeader() {}

      send() {
        this.onload?.();
      }
    }
    vi.stubGlobal('XMLHttpRequest', MockXHR);

    const progress = vi.fn();
    const blobInfo = {
      blob: () => new File(['b'], 'from-blob.jpg', { type: 'image/jpeg' }),
      filename: () => 'from-blob.jpg',
    };

    const url = await window.djangoTinyMCEImagesUploadHandler(blobInfo, progress);
    expect(url).toBe('/media/handler.jpg');
  });
});
