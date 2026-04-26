import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SelectController, SelectSearchableController } from './select-search.js';
import { buildSelectMarkup } from '../test/fixtures.js';

describe('SelectController', () => {
  let root;
  let native;

  beforeEach(() => {
    document.body.innerHTML = buildSelectMarkup({ searchable: false });
    root = document.getElementById('sel-root');
    native = document.getElementById('id_test_select');
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('init синхронизирует подпись с выбранной опцией', () => {
    const c = new SelectController(root);
    c.init();
    const label = root.querySelector('[data-mg-part="toggle-label"]');
    expect(label.textContent).toBe('Бета');
  });

  it('открытие по клику и выбор другой опции', () => {
    const c = new SelectController(root);
    c.init();
    const toggle = root.querySelector('[data-mg-part="toggle"]');
    const dd = root.querySelector('[data-mg-part="dropdown"]');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dd.classList.contains('hidden')).toBe(false);

    const optionNodes = root.querySelectorAll('[data-mg-part="option"]');
    const first = optionNodes[0];
    first.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(native.value).toBe('a');
    expect(dd.classList.contains('hidden')).toBe(true);
  });

  it('шлёт mg:select:select при выборе', () => {
    const c = new SelectController(root);
    c.init();
    const handler = vi.fn();
    root.addEventListener('mg:select:select', handler);
    const toggle = root.querySelector('[data-mg-part="toggle"]');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const optionNodes = root.querySelectorAll('[data-mg-part="option"]');
    optionNodes[0].dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(handler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: expect.objectContaining({ value: 'a' }),
      }),
    );
  });

  it('Escape закрывает и фокус не падает', () => {
    const c = new SelectController(root);
    c.init();
    const toggle = root.querySelector('[data-mg-part="toggle"]');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const dd = root.querySelector('[data-mg-part="dropdown"]');
    toggle.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }));
    expect(dd.classList.contains('hidden')).toBe(true);
  });

  it('disabled на native отключает toggle', () => {
    const c = new SelectController(root);
    c.init();
    native.disabled = true;
    native.dispatchEvent(new Event('change', { bubbles: true }));
    const toggle = root.querySelector('[data-mg-part="toggle"]');
    expect(toggle.disabled).toBe(true);
  });

  it('destroy снимает observer и обработчики', () => {
    const c = new SelectController(root);
    c.init();
    c.destroy();
    expect(() => {
      native.dispatchEvent(new Event('change', { bubbles: true }));
    }).not.toThrow();
  });
});

describe('SelectSearchableController', () => {
  let root;
  let native;

  beforeEach(() => {
    document.body.innerHTML = buildSelectMarkup({ searchable: true });
    root = document.getElementById('sel-root');
    native = document.getElementById('id_test_select');
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('фильтрует опции по полю поиска', () => {
    const c = new SelectSearchableController(root);
    c.init();
    const toggle = root.querySelector('[data-mg-part="toggle"]');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const search = root.querySelector('[data-mg-part="search-input"]');
    search.value = 'Гам';
    search.dispatchEvent(new Event('input', { bubbles: true }));
    const visible = root.querySelectorAll('[data-mg-part="option"]');
    expect(visible.length).toBe(1);
    expect(visible[0].textContent).toContain('Гамма');
  });

  it('при закрытии сбрасывает строку поиска', () => {
    const c = new SelectSearchableController(root);
    c.init();
    const toggle = root.querySelector('[data-mg-part="toggle"]');
    const search = root.querySelector('[data-mg-part="search-input"]');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    search.value = 'ыы';
    search.dispatchEvent(new Event('input', { bubbles: true }));
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(search.value).toBe('');
  });
});
