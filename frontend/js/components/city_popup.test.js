// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { describe, expect, it, vi } from 'vitest';

vi.mock('leaflet', () => ({
    default: { Path: class Path {} },
}));

import { bindPopupToLayer } from './city_popup.js';

const cityData = {
    id: 1,
    name: 'Тестовый город',
    regionName: 'Тестовый регион',
    countryName: 'Россия',
    isVisited: false,
    firstVisitDate: '',
    lastVisitDate: '',
    numberOfVisits: 1,
    numberOfUsersWhoVisitCity: null,
    numberOfVisitsAllUsers: null,
};

function createLayer() {
    return {
        bindPopup: vi.fn(),
        bindTooltip: vi.fn(),
        on: vi.fn(),
    };
}

describe('bindPopupToLayer', () => {
    it('сохраняет немедленное построение popup по умолчанию', () => {
        const layer = createLayer();

        bindPopupToLayer(layer, cityData, { isAuthenticated: true });

        expect(layer.bindPopup.mock.calls[0][0]).toEqual(expect.any(String));
    });

    it('передаёт Leaflet ленивую функцию и кеширует построенный HTML', () => {
        const layer = createLayer();
        const mutableCityData = { ...cityData };

        bindPopupToLayer(layer, mutableCityData, {
            isAuthenticated: true,
            lazyPopup: true,
        });

        const contentFactory = layer.bindPopup.mock.calls[0][0];
        expect(contentFactory).toEqual(expect.any(Function));

        mutableCityData.name = 'Город перед первым открытием';
        const firstContent = contentFactory();
        expect(firstContent).toContain('Город перед первым открытием');

        mutableCityData.name = 'Город перед повторным открытием';
        const secondContent = contentFactory();
        expect(secondContent).toBe(firstContent);
        expect(secondContent).not.toContain('Город перед повторным открытием');
    });
});
