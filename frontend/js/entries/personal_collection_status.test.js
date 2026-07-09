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

    expect(showDaisyToast).toHaveBeenCalledWith(
      'success',
      'Ссылка на коллекцию успешно скопирована в буфер обмена',
    );
    expect(showSuccessToast).not.toHaveBeenCalled();
  });
});
