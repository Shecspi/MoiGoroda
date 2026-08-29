// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { beforeEach, describe, expect, it, vi } from 'vitest';

const showSuccessToast = vi.fn();
const showDangerToast = vi.fn();
const showDaisyToast = vi.fn();

vi.mock('../components/toast.js', () => ({
  showSuccessToast,
  showDangerToast,
}));

vi.mock('../components/daisyui_toast.js', () => ({
  showDaisyToast,
}));

vi.mock('../components/get_cookie.js', () => ({
  getCookie: () => 'csrf-token',
}));

describe('personal_collection_status', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    document.body.innerHTML = '';

    Object.defineProperty(navigator, 'share', {
      configurable: true,
      value: undefined,
    });
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  async function loadPersonalCollectionStatus() {
    await import('./personal_collection_status.js');
    document.dispatchEvent(new Event('DOMContentLoaded'));
    window.dispatchEvent(new Event('load'));
  }

  it('показывает daisyUI toast после копирования ссылки в буфер обмена', async () => {
    document.body.innerHTML = `
      <button
        id="copy-collection-link-button"
        data-collection-url="/collection/personal/collection-id/list"
        data-collection-title="Моя коллекция"
      >
        <svg id="copy-collection-link-icon"></svg>
      </button>
    `;

    await loadPersonalCollectionStatus();
    document.getElementById('copy-collection-link-button').click();
    await vi.waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        'http://localhost:3000/collection/personal/collection-id/list',
      );
    });

    expect(showDaisyToast).toHaveBeenCalledWith({
      type: 'success',
      content: 'Ссылка на коллекцию успешно скопирована в буфер обмена',
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });
    expect(showSuccessToast).not.toHaveBeenCalled();
  });

  it('повторно инициализирует owner controls после обновления списка без дублирования обработчика', async () => {
    document.body.innerHTML = `
      <section data-visited-city-refresh>
        <input id="collection-public-status-switch" data-collection-id="collection-id" type="checkbox">
      </section>
    `;
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({is_public: true}),
    });

    await loadPersonalCollectionStatus();
    document.body.innerHTML = `
      <section data-visited-city-refresh>
        <input id="collection-public-status-switch" data-collection-id="collection-id" type="checkbox">
      </section>
    `;
    const root = document.querySelector('[data-visited-city-refresh]');
    document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
    document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));

    const switchElement = document.getElementById('collection-public-status-switch');
    switchElement.checked = true;
    switchElement.dispatchEvent(new Event('change'));

    await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(fetch).toHaveBeenCalledWith(
      '/api/collection/personal/collection-id/update-public-status',
      expect.objectContaining({method: 'PATCH'}),
    );
  });
});
