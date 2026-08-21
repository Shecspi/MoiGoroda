// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    addRegionCityDisplayControl: vi.fn(),
    bindPopupToMarker: vi.fn(),
    map: {
        fitBounds: vi.fn(),
        hasLayer: vi.fn(),
        removeControl: vi.fn(),
    },
    marker: {
        off: vi.fn(),
        setIcon: vi.fn(),
        unbindPopup: vi.fn(),
        unbindTooltip: vi.fn(),
    },
    markersGroup: {
        addLayer: vi.fn(),
        addTo: vi.fn(),
        getBounds: vi.fn(),
        getLayers: vi.fn(() => [mocks.marker]),
        hasLayer: vi.fn(),
        removeLayer: vi.fn(),
    },
    regionPolygon: {addTo: vi.fn(), getBounds: vi.fn()},
}));

vi.mock('leaflet', () => ({
    default: {
        featureGroup: vi.fn(() => mocks.markersGroup),
        geoJSON: vi.fn(() => mocks.regionPolygon),
        marker: vi.fn(() => mocks.marker),
    },
}));
vi.mock('../components/map.js', () => ({
    addErrorControl: vi.fn(),
    addLoadControl: vi.fn(),
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
vi.mock('../components/region_city_display_control.js', () => ({
    addRegionCityDisplayControl: mocks.addRegionCityDisplayControl,
    syncRegionCityDisplayControl: vi.fn(),
}));
vi.mock('../components/region_city_polygons.js', () => ({
    buildRegionPolygonUrl: vi.fn(() => '/region-polygon'),
    loadCityPolygonLayers: vi.fn(),
    updateCityPolygonLayer: vi.fn(),
}));

describe('map_region_selected', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        mocks.regionPolygon.addTo.mockReturnValue(mocks.regionPolygon);
        document.body.innerHTML = `
            <span id="iso3166_code" data-iso3166_code="RU-TVE"></span>
            <span class="js-visited-cities-stat"><strong>1</strong></span>
            <span id="visited-cities-word">город</span>
            <span id="visited-word">Посещён</span>`;
        window.ALL_CITIES = [{
            id: 42,
            name: 'Тверь',
            lat: 56.8596,
            lon: 35.9119,
            isVisited: false,
        }];
        window.IS_AUTHENTICATED = true;
        window.URL_S3_GEO_POLYGONS = 'https://example.test/geo';
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({}),
        }));
    });

    afterEach(() => {
        document.body.innerHTML = '';
        delete window.ALL_CITIES;
        delete window.IS_AUTHENTICATED;
        delete window.URL_S3_GEO_POLYGONS;
        delete window.MG_MAIN_MAP;
        vi.unstubAllGlobals();
    });

    async function initializeMap() {
        await import('./map_region_selected.js');
        await Promise.resolve();
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
