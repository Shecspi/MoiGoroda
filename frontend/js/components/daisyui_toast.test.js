// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { showDaisyToast } from './daisyui_toast.js';

describe('showDaisyToast', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    vi.clearAllTimers();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders message as text instead of HTML', () => {
    showDaisyToast('error', '<img src=x onerror="window.__toastXss = true">Ошибка');

    const alert = document.querySelector('[role="alert"]');

    expect(alert).not.toBeNull();
    expect(alert.querySelector('img')).toBeNull();
    expect(alert.textContent).toContain('<img src=x onerror="window.__toastXss = true">Ошибка');
  });
});
