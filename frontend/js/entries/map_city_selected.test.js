// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    cityPolygon: {addTo: vi.fn(), getBounds: vi.fn(), setStyle: vi.fn()},
    marker: {addTo: vi.fn(), bindTooltip: vi.fn(), setIcon: vi.fn()},
    map: {fitBounds: vi.fn(), invalidateSize: vi.fn()},
}));

vi.mock('../components/map', () => ({
    create_map: vi.fn(() => mocks.map),
}));
vi.mock('../components/icons', () => ({
    icon_blue_pin: {name: 'blue'},
    icon_not_visited_pin: {name: 'not-visited'},
    icon_visited_pin: {name: 'visited'},
}));
vi.mock('../components/region_city_polygons', () => ({
    buildCityPolygonUrl: vi.fn(() => '/city-polygon'),
    buildCountryPolygonUrl: vi.fn(() => '/country-polygon'),
    buildRegionPolygonUrl: vi.fn(() => '/region-polygon'),
    getCityPolygonStyle: vi.fn(),
}));
vi.mock('leaflet', () => ({
    default: {
        featureGroup: vi.fn(() => ({getBounds: vi.fn()})),
        geoJSON: vi.fn(() => mocks.cityPolygon),
        marker: vi.fn(() => mocks.marker),
    },
}));

describe('map_city_selected', () => {
    let clickListeners;

    beforeEach(async () => {
        clickListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'click') {
                clickListeners.push(args[1]);
            }

            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        mocks.cityPolygon.addTo.mockReturnValue(mocks.cityPolygon);
        mocks.marker.addTo.mockReturnValue(mocks.marker);
        document.body.innerHTML = `
            <form id="deleteCityForm"></form>
            <span id="cityTitleOnModal"></span>
            <section id="user-visits"></section>
            <dialog id="mapModal"></dialog>`;
        window.IS_AUTHENTICATED = true;
        window.IS_VISITED = false;
        window.CITY_TITLE = 'Тверь';
        window.CITY_ID = 42;
        window.COUNTRY_CODE = 'RU';
        window.ISO3166 = 'RU-TVE';
        window.LAT = '56.8596';
        window.LON = '35.9119';
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({}),
        }));
        await import('./map_city_selected.js');
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    afterEach(() => {
        clickListeners.forEach((listener) => document.removeEventListener('click', listener));
        document.addEventListener.mockRestore();
        document.body.innerHTML = '';
        vi.unstubAllGlobals();
    });

    async function openMap() {
        const modal = document.querySelector('#mapModal');
        modal.classList.add('open');
        await new Promise((resolve) => setTimeout(resolve, 120));
        await new Promise((resolve) => setTimeout(resolve, 0));
    }

    it('fills the delete modal for a visit added by a replacement fragment', () => {
        document.querySelector('#user-visits').innerHTML = `
            <button class="delete_city" data-delete_url="/city/delete/18" data-city_title="Тверь"></button>`;

        document.querySelector('.delete_city').click();

        expect(document.querySelector('#deleteCityForm').action).toBe(`${window.location.origin}/city/delete/18`);
        expect(document.querySelector('#cityTitleOnModal').textContent).toBe('Тверь');
    });

    it('creates visited marker and polygon when city-added occurs before the lazy map initialization', async () => {
        const {getCityPolygonStyle} = await import('../components/region_city_polygons');
        getCityPolygonStyle.mockReturnValue({fillColor: 'green'});
        document.dispatchEvent(new CustomEvent('city-added', {
            detail: {city: {id: 42, name: 'Тверь'}},
        }));

        await openMap();

        const L = (await import('leaflet')).default;
        const {icon_visited_pin} = await import('../components/icons');
        expect(L.marker).toHaveBeenCalledWith([56.8596, 35.9119], {icon: icon_visited_pin});
        expect(getCityPolygonStyle).toHaveBeenCalledWith({isVisited: true});
    });

    it('updates existing marker and polygon when visited-city-updated occurs after map open', async () => {
        await openMap();
        const {icon_visited_pin} = await import('../components/icons');
        const {getCityPolygonStyle} = await import('../components/region_city_polygons');
        const visitedStyle = {fillColor: 'green'};
        getCityPolygonStyle.mockClear();
        getCityPolygonStyle.mockReturnValue(visitedStyle);

        document.dispatchEvent(new CustomEvent('visited-city-updated', {
            detail: {city: {id: 42, name: 'Тверь'}},
        }));

        expect(mocks.marker.setIcon).toHaveBeenCalledWith(icon_visited_pin);
        expect(mocks.cityPolygon.setStyle).toHaveBeenCalledWith(visitedStyle);
    });
});
