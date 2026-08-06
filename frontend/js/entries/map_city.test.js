// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
    actions: {
        ownCities: [],
        stateNotVisitedCities: new Map(),
        isNotVisitedClusteringEnabled: vi.fn(),
        isNotVisitedCitiesVisible: vi.fn(),
        toggleNotVisitedClustering: vi.fn(),
        subscribeNotVisitedVisibility: vi.fn(),
        removeNotVisitedMarker: vi.fn(),
    },
    addExternalBorderControl: vi.fn(),
    addInternalBorderControl: vi.fn(),
    addNotVisitedClusteringControl: vi.fn(),
    createMap: vi.fn(),
    initCountrySelect: vi.fn(),
    map: {
        setView: vi.fn(),
    },
    syncNotVisitedClusteringControl: vi.fn(),
    ToolbarActions: vi.fn(),
}));

vi.mock('leaflet', () => ({
    default: {
        featureGroup: vi.fn(),
    },
}));

vi.mock('../components/map.js', () => ({
    addExternalBorderControl: mocks.addExternalBorderControl,
    addInternalBorderControl: mocks.addInternalBorderControl,
    create_map: mocks.createMap,
}));

vi.mock('../components/toolbar_actions.js', () => ({
    ToolbarActions: mocks.ToolbarActions,
}));

vi.mock('../components/initCountrySelect', () => ({
    initCountrySelect: mocks.initCountrySelect,
}));

vi.mock('../components/schemas.js', () => ({
    City: class {},
    MarkerStyle: {},
}));

vi.mock('../components/toast.js', () => ({
    showDangerToast: vi.fn(),
}));

vi.mock('../components/not_visited_clustering_control.js', () => ({
    addNotVisitedClusteringControl: mocks.addNotVisitedClusteringControl,
    syncNotVisitedClusteringControl: mocks.syncNotVisitedClusteringControl,
}));

describe('map_city', () => {
    let cityAddedListeners;

    beforeEach(() => {
        cityAddedListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'city-added') {
                cityAddedListeners.push(args[1]);
            }

            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        document.body.innerHTML = '';
        window.history.replaceState({}, '', '/');
        window.URL_GET_VISITED_CITIES = '/api/city/visited';
        mocks.actions.ownCities = [];
        mocks.actions.stateNotVisitedCities.clear();
        mocks.createMap.mockReturnValue(mocks.map);
        mocks.ToolbarActions.mockImplementation(() => mocks.actions);
        mocks.initCountrySelect.mockResolvedValue();
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([]),
        }));
    });

    afterEach(() => {
        cityAddedListeners.forEach((listener) => {
            document.removeEventListener('city-added', listener);
        });
        document.addEventListener.mockRestore();
        window.onload = null;
        delete window.URL_GET_VISITED_CITIES;
        delete window.MG_MAIN_MAP;
        delete window.filterCitiesByYear;
        delete window.updateNotVisitedCitiesButtonState;
        vi.unstubAllGlobals();
    });

    async function initializeMapCity() {
        await import('./map_city.js');
        await window.onload();
    }

    it('связывает контрол кластеризации с ToolbarActions', async () => {
        const control = { id: 'clustering-control' };
        const toggleResult = Promise.resolve(true);
        mocks.actions.isNotVisitedClusteringEnabled.mockReturnValue(true);
        mocks.actions.isNotVisitedCitiesVisible.mockReturnValue(false);
        mocks.actions.toggleNotVisitedClustering.mockReturnValue(toggleResult);
        mocks.addNotVisitedClusteringControl.mockReturnValue(control);

        await initializeMapCity();

        const [map, callbacks] = mocks.addNotVisitedClusteringControl.mock.calls[0];
        expect(map).toBe(mocks.map);
        expect(callbacks.getEnabled()).toBe(true);
        expect(callbacks.getVisible()).toBe(false);
        expect(callbacks.onToggle()).toBe(toggleResult);

        const visibilityListener = mocks.actions.subscribeNotVisitedVisibility.mock.calls[0][0];
        visibilityListener();
        expect(mocks.syncNotVisitedClusteringControl).toHaveBeenCalledWith(control);
    });

    it('удаляет непосещённый маркер через ToolbarActions после добавления города', async () => {
        await initializeMapCity();

        await new Promise((resolve) => {
            mocks.actions.removeNotVisitedMarker.mockImplementationOnce(resolve);

            document.dispatchEvent(new CustomEvent('city-added', {
                detail: {city: {id: 123, name: 'Город'}},
            }));
        });

        expect(mocks.actions.removeNotVisitedMarker).toHaveBeenCalledWith(123);
    });
});
