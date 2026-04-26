import { describe, it, expect, beforeEach } from 'vitest';
import { registerDefaultComponents } from '../index.js';
import { initAll, destroyAll } from './init.js';
import { buildStaticComboboxMarkup } from '../test/fixtures.js';

describe('initAll / destroyAll', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    registerDefaultComponents();
  });

  it('initAll находит data-component и инициализирует mg-combobox-static', () => {
    document.body.innerHTML = buildStaticComboboxMarkup();
    initAll();
    const input = document.querySelector('[data-mg-part="input"]');
    expect(input.getAttribute('role')).toBe('combobox');
  });

  it('повторный initAll не пересоздаёт экземпляр (уже uiBound)', () => {
    document.body.innerHTML = buildStaticComboboxMarkup();
    const root = document.getElementById('cb-root');
    initAll();
    expect(root.dataset.uiBound).toBe('1');
    initAll();
    expect(root.dataset.uiBound).toBe('1');
  });

  it('destroyAll сбрасывает data-ui-bound', () => {
    document.body.innerHTML = buildStaticComboboxMarkup();
    const root = document.getElementById('cb-root');
    initAll();
    expect(root.dataset.uiBound).toBe('1');
    destroyAll();
    expect(root.dataset.uiBound).toBeUndefined();
  });
});
