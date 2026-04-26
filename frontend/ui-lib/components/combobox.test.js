import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { StaticComboboxController, RemoteComboboxController } from './combobox.js';
import { buildStaticComboboxMarkup, buildRemoteComboboxMarkup } from '../test/fixtures.js';

/**
 * @param {number} [ms=0]
 * @returns {Promise<void>}
 */
function delay(ms = 0) {
  return new Promise((r) => setTimeout(r, ms));
}

describe('StaticComboboxController', () => {
  let root;

  beforeEach(() => {
    document.body.innerHTML = buildStaticComboboxMarkup();
    root = document.getElementById('cb-root');
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('init выставляет a11y-атрибуты и скрывает listbox', () => {
    const c = new StaticComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    const list = root.querySelector('[data-mg-part="listbox"]');
    expect(input.getAttribute('role')).toBe('combobox');
    expect(input.getAttribute('aria-expanded')).toBe('false');
    expect(list.classList.contains('hidden')).toBe(true);
  });

  it('фильтрует опции по вводу и открывает список', () => {
    const c = new StaticComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    input.value = 'тве';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    const visible = root.querySelectorAll(
      '[data-mg-part="option"]:not(.hidden)',
    );
    expect(visible.length).toBe(1);
    expect(visible[0].textContent).toContain('Тверь');
  });

  it('клик по опции обновляет hidden, шлёт mg:combobox:select', () => {
    const c = new StaticComboboxController(root);
    c.init();
    const hidden = root.querySelector('[data-mg-part="hidden-input"]');
    const handler = vi.fn();
    root.addEventListener('mg:combobox:select', handler);

    const first = root.querySelectorAll('[data-mg-part="option"]')[0];
    first.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(hidden.value).toBe('1');
    expect(handler).toHaveBeenCalledWith(
      expect.objectContaining({ detail: expect.objectContaining({ value: '1', source: 'pointer' }) }),
    );
  });

  it('клавиатура: Enter выбирает первую отфильтрованную опцию и закрывает список', () => {
    const c = new StaticComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    const hidden = root.querySelector('[data-mg-part="hidden-input"]');
    const handler = vi.fn();
    root.addEventListener('mg:combobox:select', handler);

    input.value = 'мо';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true, cancelable: true }),
    );

    expect(handler).toHaveBeenCalled();
    expect(input.getAttribute('aria-expanded')).toBe('false');
  });

  it('Escape закрывает список', () => {
    const c = new StaticComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    const list = root.querySelector('[data-mg-part="listbox"]');
    input.value = 'м';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    expect(list.classList.contains('hidden')).toBe(false);
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(list.classList.contains('hidden')).toBe(true);
  });

  it('pointerdown вне root закрывает', () => {
    const c = new StaticComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    const list = root.querySelector('[data-mg-part="listbox"]');
    input.value = 'мо';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    const outside = document.createElement('div');
    document.body.appendChild(outside);
    outside.dispatchEvent(new Event('pointerdown', { bubbles: true }));
    expect(list.classList.contains('hidden')).toBe(true);
    outside.remove();
  });

  it('destroy снимает обработчики (повтор pointerdown не падает)', () => {
    const c = new StaticComboboxController(root);
    c.init();
    c.destroy();
    const outside = document.createElement('div');
    document.body.appendChild(outside);
    expect(() =>
      outside.dispatchEvent(new Event('pointerdown', { bubbles: true })),
    ).not.toThrow();
    outside.remove();
  });

  it('minChars: до порога onBelowMinChars и список закрыт', () => {
    document.body.innerHTML = buildStaticComboboxMarkup({
      options: [
        { value: '1', label: 'AA' },
        { value: '2', label: 'AB' },
      ],
    });
    const el = document.getElementById('cb-root');
    el.dataset.mgComboboxMinChars = '2';
    const c = new StaticComboboxController(el);
    c.init();
    const input = el.querySelector('[data-mg-part="input"]');
    const list = el.querySelector('[data-mg-part="listbox"]');
    input.value = 'a';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    expect(list.classList.contains('hidden')).toBe(true);
  });
});

describe('RemoteComboboxController', () => {
  let fetchMock;

  beforeEach(() => {
    document.body.innerHTML = buildRemoteComboboxMarkup({
      sourceUrl: '/api/city/search',
      minChars: '0',
      debounce: '0',
    });
    fetchMock = vi.fn();
    globalThis.fetch = fetchMock;
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('запрашивает API и рисует опции (debounce=0)', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([{ value: 10, label: 'Париж' }]),
    });
    const root = document.getElementById('cb-remote');
    const c = new RemoteComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    const list = root.querySelector('[data-mg-part="listbox"]');

    input.value = 'п';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    await vi.waitFor(
      () => {
        expect(list.textContent).toContain('Париж');
      },
      { timeout: 2000 },
    );
    expect(fetchMock).toHaveBeenCalled();
    const url = fetchMock.mock.calls[0][0];
    expect(String(url)).toContain('/api/city/search');
    expect(String(url)).toContain('query');
  });

  it('устаревший ответ не перезаписывает UI (токен запроса)', async () => {
    let finishFirst;
    const firstPromise = new Promise((resolve) => {
      finishFirst = resolve;
    });
    fetchMock
      .mockImplementationOnce(
        () =>
          firstPromise.then(() => ({
            ok: true,
            json: () => Promise.resolve([{ value: 1, label: 'Старый' }]),
          })),
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([{ value: 2, label: 'Актуальный' }]),
        }),
      );

    const root = document.getElementById('cb-remote');
    const c = new RemoteComboboxController(root);
    c.init();
    const input = root.querySelector('[data-mg-part="input"]');
    const list = root.querySelector('[data-mg-part="listbox"]');

    input.value = 'a';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    await delay(5);

    input.value = 'b';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    await vi.waitFor(() => expect(list.textContent).toContain('Актуальный'), { timeout: 2000 });

    await finishFirst();
    await delay(5);

    expect(list.textContent).toContain('Актуальный');
    expect(list.textContent).not.toContain('Старый');
  });

  it('добавляет country из location.search, если задано в корне', async () => {
    const prev = globalThis.location;
    const stub = { search: '?country=KZ', origin: 'https://test.example' };
    Object.defineProperty(globalThis, 'location', { value: stub, configurable: true });
    try {
      document.body.innerHTML = buildRemoteComboboxMarkup({
        countryParam: 'country',
      });
      fetchMock.mockResolvedValue({ ok: true, json: () => Promise.resolve([]) });
      const root = document.getElementById('cb-remote');
      const c = new RemoteComboboxController(root);
      c.init();
      const input = root.querySelector('[data-mg-part="input"]');
      input.value = 'x';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      await delay(20);
      expect(fetchMock).toHaveBeenCalled();
      const u = String(fetchMock.mock.calls[0][0]);
      expect(u).toContain('country=KZ');
    } finally {
      Object.defineProperty(globalThis, 'location', { value: prev, configurable: true, writable: true });
    }
  });

  it('destroy отменяет дебаунс и in-flight fetch', () => {
    const root = document.getElementById('cb-remote');
    const c = new RemoteComboboxController(root);
    c.init();
    c.destroy();
    expect(c.currentAbortController).toBeNull();
  });
});
