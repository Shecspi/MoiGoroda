// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

import {CityCombobox} from './city-combobox.js';

const city = {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'};

function renderCombobox() {
    document.body.innerHTML = `
        <div data-city-combobox>
            <div data-city-combobox-control>
                <input id="add-city-city" data-city-combobox-input>
                <button type="button" data-city-combobox-clear hidden></button>
                <span data-city-combobox-loading hidden></span>
            </div>
            <div data-city-combobox-positioner>
                <ul data-city-combobox-content></ul>
            </div>
        </div>`;
}

describe('CityCombobox', () => {
    beforeEach(() => {
        renderCombobox();
        vi.stubGlobal('fetch', vi.fn());
    });

    afterEach(() => {
        document.body.innerHTML = '';
        vi.unstubAllGlobals();
        vi.useRealTimers();
    });

    it('debounces one-character searches and cleans up superseded requests', async () => {
        vi.useFakeTimers();
        fetch.mockImplementation(() => new Promise(() => {}));
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');
        const loading = document.querySelector('[data-city-combobox-loading]');

        input.value = 'Ю';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.advanceTimersByTimeAsync(299);
        expect(fetch).not.toHaveBeenCalled();
        expect(loading.hidden).toBe(true);

        input.value = 'Юж';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.advanceTimersByTimeAsync(299);
        expect(fetch).not.toHaveBeenCalled();

        await vi.advanceTimersByTimeAsync(1);
        expect(fetch).toHaveBeenCalledOnce();
        expect(fetch.mock.calls[0][0]).toBe('/api/city/search?query=%D0%AE%D0%B6');
        expect(loading.hidden).toBe(false);
        const firstSignal = fetch.mock.calls[0][1].signal;

        input.value = 'Южн';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        expect(firstSignal.aborted).toBe(true);
        expect(loading.hidden).toBe(true);
        await vi.advanceTimersByTimeAsync(300);
        expect(fetch).toHaveBeenCalledTimes(2);

        input.value = '   ';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        expect(fetch.mock.calls[1][1].signal.aborted).toBe(true);
        expect(loading.hidden).toBe(true);
        await vi.advanceTimersByTimeAsync(300);
        expect(fetch).toHaveBeenCalledTimes(2);
    });

    it('opens matching results automatically and selects a city with a pointer', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([city]),
        });
        const onSelect = vi.fn();
        const cityCombobox = new CityCombobox(document, {onSelect});
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));

        await vi.waitFor(() => expect(input.value).toBe('Моск'));
        await vi.waitFor(() => expect(document.querySelector('[role="option"]')).not.toBeNull());
        expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(false);
        expect(document.querySelector('[role="option"]').textContent).toContain('Москва');
        expect(document.querySelector('[role="option"]').textContent).toContain('Россия');

        document.querySelector('[role="option"]').click();

        await vi.waitFor(() => expect(onSelect).toHaveBeenLastCalledWith(city));
        expect(input.value).toBe('Москва');
        expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(true);
    });

    it('keeps current results visible until a refined search finishes', async () => {
        const refinedCity = {id: 77, title: 'Мосальск', region: 'Калужская область', country: 'Россия'};
        let resolveRefinedSearch;
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([city]),
            })
            .mockImplementationOnce(() => new Promise((resolve) => {
                resolveRefinedSearch = resolve;
            }));
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');
        const loading = document.querySelector('[data-city-combobox-loading]');

        input.value = 'Мос';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[role="option"]')?.textContent).toContain('Москва'));

        input.value = 'Моса';
        input.dispatchEvent(new Event('input', {bubbles: true}));

        const currentOption = document.querySelector('[role="option"]');
        expect(currentOption).not.toBeNull();
        expect(currentOption.textContent).toContain('Москва');
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
        expect(loading.hidden).toBe(false);
        expect(document.querySelector('[role="option"]')?.textContent).toContain('Москва');

        resolveRefinedSearch({
            ok: true,
            json: vi.fn().mockResolvedValue([refinedCity]),
        });

        await vi.waitFor(() => expect(document.querySelector('[role="option"]')?.textContent).toContain('Мосальск'));
        expect(document.querySelector('[role="option"]')?.textContent).not.toContain('Москва');
    });

    it('discards current results when the refined query is blank', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([city]),
        });
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');
        const results = document.querySelector('[data-city-combobox-content]');

        input.value = 'Мос';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[role="option"]')).not.toBeNull());

        input.value = '   ';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => {
            expect(results.hidden).toBe(true);
            expect(document.querySelector('[role="option"]')).toBeNull();
        });

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true}));

        expect(document.querySelector('[role="option"]')).toBeNull();
        expect(fetch).toHaveBeenCalledOnce();
    });

    it('shows a disabled message when a remote city search has no matches', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([]),
        });
        const onSelect = vi.fn();
        const cityCombobox = new CityCombobox(document, {onSelect});
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        input.value = 'Тула';
        input.dispatchEvent(new Event('input', {bubbles: true}));

        const emptyState = await vi.waitFor(() => {
            const node = document.querySelector('[data-city-combobox-empty]');
            expect(node).not.toBeNull();
            return node;
        });
        expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(false);
        expect(emptyState.textContent).toContain('Города не найдены');
        expect(emptyState.getAttribute('role')).toBe('option');
        expect(emptyState.getAttribute('aria-disabled')).toBe('true');
        onSelect.mockClear();
        emptyState.click();
        expect(onSelect).not.toHaveBeenCalled();
    });

    it('clears an open city query and keeps focus in the input', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([city]),
        });
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');
        const clearButton = document.querySelector('[data-city-combobox-clear]');

        input.focus();
        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(false));
        expect(clearButton.hidden).toBe(false);

        clearButton.click();

        expect(input.value).toBe('');
        await vi.waitFor(() => {
            expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(true);
            expect(clearButton.hidden).toBe(true);
        });
        expect(document.activeElement).toBe(input);
    });

    it('selects the first matching city with Enter and dismisses with Escape', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([city]),
        });
        const onSelect = vi.fn();
        const cityCombobox = new CityCombobox(document, {onSelect});
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[role="option"]')).not.toBeNull());

        await vi.waitFor(() => expect(input.getAttribute('aria-activedescendant')).not.toBeNull());
        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
        await vi.waitFor(() => expect(onSelect).toHaveBeenLastCalledWith(city));

        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(false));
        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(true));
    });

    it('dismisses an open list after an outside pointer interaction', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([city]),
        });
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(false));
        const outside = document.createElement('button');
        document.body.append(outside);
        outside.dispatchEvent(new Event('pointerdown', {bubbles: true}));
        await vi.waitFor(() => expect(document.querySelector('[data-city-combobox-content]').hidden).toBe(true));
    });

    it('does not search whitespace and aborts when destroyed', async () => {
        fetch.mockImplementation(() => new Promise(() => {}));
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        input.value = '   ';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await Promise.resolve();
        expect(fetch).not.toHaveBeenCalled();

        input.value = 'М';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        const signal = fetch.mock.calls[0][1].signal;

        cityCombobox.destroy();

        expect(signal.aborted).toBe(true);
        expect(cityCombobox.machine).toBeNull();
    });

});
