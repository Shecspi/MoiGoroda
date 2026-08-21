// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    bindPopupToMarker: vi.fn(),
    map: {fitBounds: vi.fn(), setView: vi.fn()},
    marker: {
        addTo: vi.fn(),
        off: vi.fn(),
        setIcon: vi.fn(),
        unbindPopup: vi.fn(),
        unbindTooltip: vi.fn(),
    },
}));

vi.mock('leaflet', () => ({
    default: {
        featureGroup: vi.fn(() => ({getBounds: vi.fn()})),
        marker: vi.fn(() => mocks.marker),
    },
}));
vi.mock('../components/map.js', () => ({
    create_map: vi.fn(() => mocks.map),
}));
vi.mock('../components/icons.js', () => ({
    icon_not_visited_pin: {name: 'not-visited'},
    icon_visited_pin: {name: 'visited'},
}));
vi.mock('../components/city_popup.js', () => ({
    bindPopupToMarker: mocks.bindPopupToMarker,
}));
vi.mock('../components/search_services.js', () => ({
    pluralize: vi.fn(() => 'города'),
}));

describe('map_collection', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        mocks.marker.addTo.mockReturnValue(mocks.marker);
        document.body.innerHTML = `
            <span class="js-visited-cities-stat"><strong>1</strong></span>
            <span id="visited-cities-word">город</span>
            <span id="visited-word">Посещён</span>`;
        window.ALL_CITIES = [{
            id: 42,
            name: 'Тверь',
            lat: 56.8596,
            lon: 35.9119,
            isVisited: false,
            regionId: 69,
            regionName: 'Тверская область',
            countryCode: 'RU',
            countryName: 'Россия',
        }];
        window.IS_AUTHENTICATED = true;
    });

    afterEach(() => {
        document.body.innerHTML = '';
        delete window.ALL_CITIES;
        delete window.IS_AUTHENTICATED;
        delete window.MG_MAIN_MAP;
    });

    async function initializeMap() {
        await import('./map_collection.js');
        vi.clearAllMocks();
    }

    it('updates marker, popup and badge for a represented event city', async () => {
        await initializeMap();
        const {icon_visited_pin} = await import('../components/icons.js');

        document.dispatchEvent(new CustomEvent('city-added', {
            detail: {
                city: {
                    id: 42,
                    number_of_visits: 1,
                    first_visit_date: '2026-08-21',
                    last_visit_date: '2026-08-21',
                },
            },
        }));

        expect(mocks.marker.setIcon).toHaveBeenCalledWith(icon_visited_pin);
        expect(mocks.bindPopupToMarker).toHaveBeenCalledWith(
            mocks.marker,
            expect.objectContaining({id: 42, isVisited: true, numberOfVisits: 1}),
            expect.any(Object),
        );
        expect(document.querySelector('.js-visited-cities-stat strong').textContent).toBe('2');
    });

    it('does not change marker, popup or badge for an absent event city', async () => {
        await initializeMap();

        document.dispatchEvent(new CustomEvent('city-added', {
            detail: {city: {id: 99, number_of_visits: 1}},
        }));

        expect(mocks.marker.setIcon).not.toHaveBeenCalled();
        expect(mocks.bindPopupToMarker).not.toHaveBeenCalled();
        expect(document.querySelector('.js-visited-cities-stat strong').textContent).toBe('1');
    });
});
