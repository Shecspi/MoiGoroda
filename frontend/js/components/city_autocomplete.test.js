/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

import {CityAutocomplete} from './city_autocomplete.js';

describe('CityAutocomplete', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div data-city-autocomplete>
                <input data-city-autocomplete-input>
                <span data-city-autocomplete-loading hidden></span>
                <ul data-city-autocomplete-results hidden></ul>
            </div>`;
        vi.stubGlobal('fetch', vi.fn());
    });

    afterEach(() => {
        document.body.innerHTML = '';
        vi.unstubAllGlobals();
    });

    it('filters by country code when no region is selected', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
            ]),
        });
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root);
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        autocomplete.setFilters({country: 'RU'});
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());

        expect(fetch.mock.calls[0][0]).toBe(
            '/api/city/search?query=%D0%9C%D0%BE%D1%81%D0%BA&country=RU',
        );
    });

    it('sends only the region code when a region is selected', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
            ]),
        });
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root);
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        autocomplete.setFilters({country: 'RU', region: 'RU-MOW'});
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());

        expect(fetch.mock.calls[0][0]).toBe(
            '/api/city/search?query=%D0%9C%D0%BE%D1%81%D0%BA&region=RU-MOW',
        );
    });

    it('reports the chosen suggestion and keeps its city title in the input', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
            ]),
        });
        const onSelect = vi.fn();
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root, {onSelect});
        autocomplete.init();

        const input = root.querySelector('[data-city-autocomplete-input]');
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));

        await vi.waitFor(() => expect(root.querySelector('[role="option"]')).not.toBeNull());
        root.querySelector('[role="option"]').click();

        expect(input.value).toBe('Москва');
        expect(onSelect).toHaveBeenCalledWith({
            id: 42,
            title: 'Москва',
            region: 'Москва',
            country: 'Россия',
        });
        expect(root.querySelector('[data-city-autocomplete-results]').hidden).toBe(true);
    });

    it('navigates suggestions with arrows and selects the active city with Enter', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
                {id: 43, title: 'Московский', region: 'Москва', country: 'Россия'},
            ]),
        });
        const onSelect = vi.fn();
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root, {onSelect});
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(root.querySelectorAll('[role="option"]')).toHaveLength(2));

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true}));
        const options = root.querySelectorAll('[role="option"]');
        expect(options[0].classList).toContain('dui-menu-focus');
        expect(options[0].getAttribute('aria-selected')).toBe('true');

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true}));
        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowUp', bubbles: true}));
        expect(options[0].getAttribute('aria-selected')).toBe('true');

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
        expect(input.value).toBe('Москва');
        expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({id: 42}));
    });

    it('activates the last suggestion when ArrowUp is pressed first', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
                {id: 43, title: 'Московский', region: 'Москва', country: 'Россия'},
            ]),
        });
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root);
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(root.querySelectorAll('[role="option"]')).toHaveLength(2));

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowUp', bubbles: true}));

        const options = root.querySelectorAll('[role="option"]');
        expect(options[0].getAttribute('aria-selected')).toBe('false');
        expect(options[1].getAttribute('aria-selected')).toBe('true');
    });

    it('does not handle Enter before a suggestion is active', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
            ]),
        });
        const onSelect = vi.fn();
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root, {onSelect});
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(root.querySelector('[role="option"]')).not.toBeNull());
        onSelect.mockClear();
        const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            bubbles: true,
            cancelable: true,
        });

        input.dispatchEvent(event);

        expect(event.defaultPrevented).toBe(false);
        expect(onSelect).not.toHaveBeenCalled();
        expect(root.querySelector('[role="option"]').getAttribute('aria-selected')).toBe('false');
    });

    it('closes visible suggestions with Escape', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
            ]),
        });
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root);
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(root.querySelector('[role="option"]')).not.toBeNull());

        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));

        expect(root.querySelector('[data-city-autocomplete-results]').hidden).toBe(true);
    });

    it('aborts an outstanding request when the location filters change', async () => {
        let resolveSearch;
        fetch.mockImplementation(() => new Promise((resolve) => {
            resolveSearch = resolve;
        }));
        const root = document.querySelector('[data-city-autocomplete]');
        const autocomplete = new CityAutocomplete(root);
        autocomplete.init();
        const input = root.querySelector('[data-city-autocomplete-input]');
        input.value = 'Моск';
        input.dispatchEvent(new Event('input'));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        const firstSignal = fetch.mock.calls[0][1].signal;

        autocomplete.setFilters({country: 'RU', region: 'RU-MOW'});
        resolveSearch({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
            ]),
        });

        expect(firstSignal.aborted).toBe(true);
        await Promise.resolve();
        expect(root.querySelector('[data-city-autocomplete-results]').hidden).toBe(true);
    });
});
