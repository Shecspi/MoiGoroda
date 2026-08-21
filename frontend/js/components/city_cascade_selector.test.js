/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { CityCascadeSelector } from './city_cascade_selector.js';

describe('CityCascadeSelector', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <select data-city-country></select>
            <select data-city-region></select>
            <select data-city></select>`;
        vi.stubGlobal('fetch', vi.fn());
    });

    afterEach(() => {
        document.body.innerHTML = '';
        vi.unstubAllGlobals();
    });

    it('loads countries then cities for a country without regions', async () => {
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, name: 'Россия'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 10, title: 'Москва'}]),
            });
        const onChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {onChange});

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = '1';
        country.dispatchEvent(new Event('change'));

        await vi.waitFor(() => {
            expect(document.querySelector('[data-city]').value).toBe('10');
        });

        expect(fetch.mock.calls[0][0]).toBe('/api/country/list_by_cities');
        expect(fetch.mock.calls[1][0]).toBe('/api/region/list?country_id=1');
        expect(fetch.mock.calls[2][0]).toBe('/api/city/list_by_country?country_id=1');
        expect(onChange).toHaveBeenLastCalledWith({
            countryId: '1',
            regionId: '',
            cityId: '10',
        });
    });

    it('keeps the city select disabled when a country has no cities', async () => {
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, name: 'Россия'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            });
        const onChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {onChange});

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = '1';
        country.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(3));

        const city = document.querySelector('[data-city]');
        expect(city.disabled).toBe(true);
        expect(city.options[0].textContent).toBe('Нет городов');
        expect(onChange).toHaveBeenLastCalledWith({
            countryId: '1',
            regionId: '',
            cityId: '',
        });
    });

    it('aborts the stale country request before loading a newly selected country', async () => {
        const selector = new CityCascadeSelector(document.body);
        await selector.init({loadCountries: false});
        const country = document.querySelector('[data-city-country]');
        country.innerHTML = '<option value="1">Россия</option><option value="2">Казахстан</option>';
        let resolveFirstRequest;
        fetch.mockImplementationOnce(() => new Promise((resolve) => {
            resolveFirstRequest = resolve;
        }));

        country.value = '1';
        country.dispatchEvent(new Event('change'));
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        const firstSignal = fetch.mock.calls[0][1].signal;

        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 20, title: 'Астана'}]),
            });
        country.value = '2';
        country.dispatchEvent(new Event('change'));

        expect(firstSignal.aborted).toBe(true);
        resolveFirstRequest({
            ok: true,
            json: vi.fn().mockResolvedValue([{id: 100, name: 'Устаревший регион'}]),
        });
        await vi.waitFor(() => {
            expect(document.querySelector('[data-city]').value).toBe('20');
        });
    });

    it('keeps country and region selection available when a city autocomplete owns the city field', async () => {
        document.querySelector('[data-city]').remove();
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, name: 'Россия'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 10, name: 'Москва'}]),
            });
        const onChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {onChange});

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = '1';
        country.dispatchEvent(new Event('change'));

        await vi.waitFor(() => {
            expect(document.querySelector('[data-city-region]').disabled).toBe(false);
        });
        expect(onChange).toHaveBeenLastCalledWith({
            countryId: '1',
            regionId: '',
            cityId: '',
        });
        expect(onChange).toHaveBeenCalledOnce();
    });

    it('reports a loading location state before fetching regions', async () => {
        const regionsRequest = new Promise(() => {});
        fetch.mockReturnValueOnce(regionsRequest);
        const onChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {onChange});

        await selector.init({loadCountries: false});
        const country = document.querySelector('[data-city-country]');
        country.innerHTML = '<option value="1">Россия</option>';
        country.value = '1';
        country.dispatchEvent(new Event('change'));

        expect(document.querySelector('[data-city-region]').options[0].textContent).toBe('Загрузка...');
        expect(onChange).toHaveBeenLastCalledWith({
            countryId: '1',
            regionId: '',
            cityId: '',
        });
    });

    it('uses ISO codes for a modal without a city select', async () => {
        document.querySelector('[data-city]').remove();
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([
                    {id: 1, code: 'RU', name: 'Россия'},
                ]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([
                    {id: 10, iso3166: 'RU-MOW', title: 'Москва'},
                ]),
            });
        const onChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onChange,
        });

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = 'RU';
        country.dispatchEvent(new Event('change'));
        await vi.waitFor(() => {
            expect(document.querySelector('[data-city-region] option[value="RU-MOW"]')).not.toBeNull();
        });
        const region = document.querySelector('[data-city-region]');
        region.value = 'RU-MOW';
        region.dispatchEvent(new Event('change'));

        expect(fetch.mock.calls[1][0]).toBe('/api/region/list/RU/');
        expect(onChange).toHaveBeenLastCalledWith({
            countryCode: 'RU',
            regionCode: 'RU-MOW',
            cityId: '',
        });
    });

    it('loads cities for a region into an external consumer without a city select', async () => {
        document.querySelector('[data-city]').remove();
        const cities = [{id: 100, title: 'Тверь', region: 'Тверская область', country: 'Россия'}];
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, code: 'RU', name: 'Россия'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 10, iso3166: 'RU-TVE', title: 'Тверская область'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue(cities),
            });
        const onCitiesChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onCitiesChange,
        });

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = 'RU';
        country.dispatchEvent(new Event('change'));
        await vi.waitFor(() => {
            expect(document.querySelector('[data-city-region] option[value="RU-TVE"]')).not.toBeNull();
        });
        const region = document.querySelector('[data-city-region]');
        region.value = 'RU-TVE';
        region.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(onCitiesChange).toHaveBeenLastCalledWith(cities));
        expect(fetch.mock.calls[2][0]).toBe('/api/city/list_by_region?region_id=10');
    });

    it('loads country cities into an external consumer when the country has no regions', async () => {
        document.querySelector('[data-city]').remove();
        const cities = [{id: 100, title: 'Никосия', region: null, country: 'Кипр'}];
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, code: 'CY', name: 'Кипр'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue(cities),
            });
        const onCitiesChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onCitiesChange,
        });

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = 'CY';
        country.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(onCitiesChange).toHaveBeenLastCalledWith(cities));
        expect(fetch.mock.calls[2][0]).toBe('/api/city/list_by_country?country_id=1');
    });

    it('uses a country numeric ID to load cities in code mode', async () => {
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([
                    {id: 1, code: 'RU', name: 'Россия'},
                ]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 10, title: 'Москва'}]),
            });
        const selector = new CityCascadeSelector(document.body, {locationValueMode: 'code'});

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = 'RU';
        country.dispatchEvent(new Event('change'));

        await vi.waitFor(() => {
            expect(document.querySelector('[data-city]').value).toBe('10');
        });

        expect(fetch.mock.calls[1][0]).toBe('/api/region/list/RU/');
        expect(fetch.mock.calls[2][0]).toBe('/api/city/list_by_country?country_id=1');
    });

    it('uses a region numeric ID to load cities in code mode', async () => {
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([
                    {id: 1, code: 'RU', name: 'Россия'},
                ]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([
                    {id: 10, iso3166: 'RU-MOW', title: 'Москва'},
                ]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 100, title: 'Тверь'}]),
            });
        const selector = new CityCascadeSelector(document.body, {locationValueMode: 'code'});

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = 'RU';
        country.dispatchEvent(new Event('change'));
        await vi.waitFor(() => {
            expect(document.querySelector('[data-city-region] option[value="RU-MOW"]')).not.toBeNull();
        });
        const region = document.querySelector('[data-city-region]');
        region.value = 'RU-MOW';
        region.dispatchEvent(new Event('change'));

        await vi.waitFor(() => {
            expect(document.querySelector('[data-city]').value).toBe('100');
        });

        expect(fetch.mock.calls[2][0]).toBe('/api/city/list_by_region?region_id=10');
    });

    it('keeps the city select disabled when a region has no cities', async () => {
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, name: 'Россия'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 10, title: 'Москва'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            });
        const onChange = vi.fn();
        const selector = new CityCascadeSelector(document.body, {onChange});

        await selector.init();
        const country = document.querySelector('[data-city-country]');
        country.value = '1';
        country.dispatchEvent(new Event('change'));
        await vi.waitFor(() => {
            expect(document.querySelector('[data-city-region] option[value="10"]')).not.toBeNull();
        });
        const region = document.querySelector('[data-city-region]');
        region.value = '10';
        region.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(3));

        const city = document.querySelector('[data-city]');
        await vi.waitFor(() => expect(city.options[0].textContent).not.toBe('Загрузка...'));
        expect(city.disabled).toBe(true);
        expect(city.options[0].textContent).toBe('Нет городов');
        expect(onChange).toHaveBeenLastCalledWith({
            countryId: '1',
            regionId: '10',
            cityId: '',
        });
    });

    it('provides code-mode option values to updateOptions', async () => {
        const updateOptions = vi.fn((select, items, placeholder, disabled, selectFirst, getOptionValue) => {
            select.replaceChildren();
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = placeholder;
            select.add(emptyOption);
            items.forEach((item) => {
                const option = document.createElement('option');
                option.value = getOptionValue(item);
                option.textContent = item.name || item.title;
                select.add(option);
            });
            select.disabled = disabled;
            select.value = selectFirst && items.length > 0 ? getOptionValue(items[0]) : '';
        });
        fetch.mockResolvedValueOnce({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 1, code: 'RU', name: 'Россия'},
            ]),
        });
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            updateOptions,
        });

        await selector.init();

        expect(document.querySelector('[data-city-country]').value).toBe('');
        expect(document.querySelector('[data-city-country] option[value="RU"]')).not.toBeNull();
    });

    it('does not let a destroyed selector overwrite countries loaded by a newer instance', async () => {
        let resolveStaleCountries;
        fetch.mockImplementationOnce(() => new Promise((resolve) => {
            resolveStaleCountries = resolve;
        }));
        const staleSelector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
        });

        const staleInit = staleSelector.init();
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        staleSelector.destroy();

        fetch.mockResolvedValueOnce({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 2, code: 'KZ', name: 'Казахстан'},
            ]),
        });
        const currentSelector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
        });
        await currentSelector.init();

        resolveStaleCountries({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 1, code: 'RU', name: 'Россия'},
            ]),
        });
        await staleInit;

        expect(Array.from(document.querySelector('[data-city-country]').options, (option) => option.value))
            .toEqual(['', 'KZ']);
    });

    it('selects a city location by codes after loading its regions', async () => {
        document.querySelector('[data-city]').remove();
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 1, code: 'RU', name: 'Россия'}]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([
                    {id: 10, iso3166: 'RU-MOW', title: 'Москва'},
                ]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 100, title: 'Москва'}]),
            });
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onCitiesChange: vi.fn(),
        });

        await selector.init();
        await selector.selectLocation({countryCode: 'RU', regionCode: 'RU-MOW'});

        expect(document.querySelector('[data-city-country]').value).toBe('RU');
        expect(document.querySelector('[data-city-region]').value).toBe('RU-MOW');
        expect(fetch.mock.calls[1][0]).toBe('/api/region/list/RU/');
        expect(fetch.mock.calls[2][0]).toBe('/api/city/list_by_region?region_id=10');
    });

    it('does not let a superseded location selection overwrite the newest location', async () => {
        document.querySelector('[data-city]').remove();
        fetch.mockResolvedValueOnce({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 1, code: 'RU', name: 'Россия'},
                {id: 2, code: 'KZ', name: 'Казахстан'},
            ]),
        });
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onCitiesChange: vi.fn(),
        });
        await selector.init();

        let resolveRussianRegions;
        fetch.mockImplementationOnce(() => new Promise((resolve) => {
            resolveRussianRegions = resolve;
        }));
        const staleSelection = selector.selectLocation({countryCode: 'RU'});
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));

        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 200, title: 'Астана'}]),
            });
        const currentSelection = selector.selectLocation({countryCode: 'KZ'});
        resolveRussianRegions({
            ok: true,
            json: vi.fn().mockResolvedValue([{id: 10, iso3166: 'RU-MOW', title: 'Москва'}]),
        });

        await expect(staleSelection).resolves.toBe(false);
        await expect(currentSelection).resolves.toBe(true);
        expect(document.querySelector('[data-city-country]').value).toBe('KZ');
        expect(document.querySelector('[data-city-region]').options[0].textContent).toBe('Нет регионов');
    });

    it('reports a failed country synchronization', async () => {
        document.querySelector('[data-city]').remove();
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: vi.fn().mockResolvedValue([{id: 8, code: 'CY', name: 'Кипр'}]),
            })
            .mockResolvedValueOnce({ok: false});
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onCitiesChange: vi.fn(),
        });

        await selector.init();

        await expect(selector.selectLocation({countryCode: 'CY'})).resolves.toBe(false);
    });

    it('cancels a pending location selection', async () => {
        document.querySelector('[data-city]').remove();
        fetch.mockResolvedValueOnce({
            ok: true,
            json: vi.fn().mockResolvedValue([{id: 1, code: 'RU', name: 'Россия'}]),
        });
        const selector = new CityCascadeSelector(document.body, {
            locationValueMode: 'code',
            onCitiesChange: vi.fn(),
        });
        await selector.init();

        let resolveRegions;
        fetch.mockImplementationOnce(() => new Promise((resolve) => {
            resolveRegions = resolve;
        }));
        const selection = selector.selectLocation({countryCode: 'RU'});
        await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));

        selector.cancelLocationSelection();
        resolveRegions({
            ok: true,
            json: vi.fn().mockResolvedValue([{id: 10, iso3166: 'RU-MOW', title: 'Москва'}]),
        });

        await expect(selection).resolves.toBe(false);
    });
});
