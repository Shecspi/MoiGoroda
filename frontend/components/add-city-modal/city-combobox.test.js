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

    it('selects the highlighted city with the keyboard and dismisses with Escape', async () => {
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

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true}));
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

    it('uses location filters and ignores an aborted stale response', async () => {
        let resolveSearch;
        fetch.mockImplementationOnce(() => new Promise((resolve) => {
            resolveSearch = resolve;
        }));
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        cityCombobox.setFilters({country: 'RU'});
        await Promise.resolve();
        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        const firstSignal = fetch.mock.calls[0][1].signal;
        expect(fetch.mock.calls[0][0]).toBe('/api/city/search?query=%D0%9C%D0%BE%D1%81%D0%BA&country=RU');

        cityCombobox.setFilters({country: 'RU', region: 'RU-MOW'});
        resolveSearch({
            ok: true,
            json: vi.fn().mockResolvedValue([city]),
        });

        expect(firstSignal.aborted).toBe(true);
        await Promise.resolve();
        expect(document.querySelector('[role="option"]')).toBeNull();
        expect(input.value).toBe('');
    });

    it('does not search below three trimmed characters and aborts when destroyed', async () => {
        fetch.mockImplementation(() => new Promise(() => {}));
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        const input = document.querySelector('[data-city-combobox-input]');

        input.value = ' Мо ';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await Promise.resolve();
        expect(fetch).not.toHaveBeenCalled();

        input.value = 'Моск';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        const signal = fetch.mock.calls[0][1].signal;

        cityCombobox.destroy();

        expect(signal.aborted).toBe(true);
        expect(cityCombobox.machine).toBeNull();
    });

    it('opens and filters preloaded location cities without remote search', async () => {
        const localCities = [
            city,
            {id: 43, title: 'Можайск', region: 'Московская область', country: 'Россия'},
        ];
        const cityCombobox = new CityCombobox(document);
        cityCombobox.init();
        cityCombobox.setCities(localCities);
        const input = document.querySelector('[data-city-combobox-input]');

        input.click();

        await vi.waitFor(() => expect(document.querySelectorAll('[role="option"]')).toHaveLength(2));
        input.value = 'жай';
        input.dispatchEvent(new Event('input', {bubbles: true}));

        await vi.waitFor(() => expect(document.querySelectorAll('[role="option"]')).toHaveLength(1));
        expect(document.querySelector('[role="option"]').textContent).toContain('Можайск');
        expect(fetch).not.toHaveBeenCalled();
    });
});
