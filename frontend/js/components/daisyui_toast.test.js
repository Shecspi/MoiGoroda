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

  it('rejects the removed positional interface', () => {
    expect(() => showDaisyToast('error', 'Ошибка')).toThrow(TypeError);
    expect(document.querySelector('[role="alert"]')).toBeNull();
  });

  it('renders string content as text instead of HTML', () => {
    showDaisyToast({
      type: 'error',
      content: '<img src=x onerror="window.__toastXss = true">Ошибка',
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });

    const alert = document.querySelector('[role="alert"]');

    expect(alert).not.toBeNull();
    expect(alert.querySelector('img')).toBeNull();
    expect(alert.textContent).toContain('<img src=x onerror="window.__toastXss = true">Ошибка');
  });

  it('preserves interactive elements from DOM content', () => {
    const content = document.createDocumentFragment();
    const link = document.createElement('a');
    link.href = '/city/42';
    link.textContent = 'Москва';
    content.append(link);

    showDaisyToast({
      type: 'success',
      content,
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });

    const renderedLink = document.querySelector('[role="alert"] a');
    expect(renderedLink).toBe(link);
    expect(renderedLink.getAttribute('href')).toBe('/city/42');
  });

  it('can be dismissed with an accessible close button', () => {
    showDaisyToast({
      type: 'success',
      content: 'Готово',
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });

    const closeButton = document.querySelector('button[aria-label="Закрыть уведомление"]');
    expect(closeButton).not.toBeNull();

    closeButton.click();

    expect(document.querySelector('[role="alert"]')).toBeNull();
    expect(document.getElementById('daisy-toast-container')).toBeNull();
  });

  it('closes automatically after the configured 5000 ms', () => {
    showDaisyToast({
      type: 'success',
      content: 'Готово',
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });

    vi.advanceTimersByTime(4999);
    expect(document.querySelector('[role="alert"]')).not.toBeNull();

    vi.advanceTimersByTime(1);
    expect(document.querySelector('[role="alert"]')).toBeNull();
  });

  it('resumes the remaining time only after hover and focus both end', () => {
    showDaisyToast({
      type: 'success',
      content: 'Готово',
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });
    const alert = document.querySelector('[role="alert"]');
    const closeButton = alert.querySelector('button');

    vi.advanceTimersByTime(2000);
    alert.dispatchEvent(new MouseEvent('mouseenter'));
    vi.advanceTimersByTime(4000);
    expect(alert.isConnected).toBe(true);

    closeButton.focus();
    alert.dispatchEvent(new MouseEvent('mouseleave'));
    vi.advanceTimersByTime(4000);
    expect(alert.isConnected).toBe(true);

    closeButton.blur();
    vi.advanceTimersByTime(2999);
    expect(alert.isConnected).toBe(true);

    vi.advanceTimersByTime(1);
    expect(alert.isConnected).toBe(false);
  });

  it('does not change the active element when shown', () => {
    const input = document.createElement('input');
    document.body.append(input);
    input.focus();

    showDaisyToast({
      type: 'success',
      content: 'Готово',
      duration: 5000,
      dismissible: true,
      pauseOnInteraction: true,
    });

    expect(document.activeElement).toBe(input);
  });
});
