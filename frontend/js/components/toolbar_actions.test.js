// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const mocks = vi.hoisted(() => ({
    marker: vi.fn(),
    bindPopupToMarker: vi.fn(),
    addErrorControl: vi.fn(),
    addLoadControl: vi.fn(() => ({ id: 'load-control' })),
}));

vi.mock('leaflet', () => ({
    default: { marker: mocks.marker },
}));
vi.mock('./icons.js', () => ({
    icon_blue_pin: {},
    icon_not_visited_pin: {},
    icon_subscription_pin: {},
    icon_together_pin: {},
    icon_visited_pin: {},
}));
vi.mock('./services.js', () => ({
    open_modal_for_add_city: vi.fn(),
    close_modal_for_add_city: vi.fn(),
}));
vi.mock('./get_cookie.js', () => ({ getCookie: () => 'csrf-token' }));
vi.mock('./map.js', () => ({
    addErrorControl: mocks.addErrorControl,
    addLoadControl: mocks.addLoadControl,
}));
vi.mock('./city_popup.js', () => ({
    bindPopupToMarker: mocks.bindPopupToMarker,
}));
vi.mock('./not_visited_city_layer.js', () => ({
    NotVisitedCityLayer: vi.fn(),
}));

import { NotVisitedCityLayer } from './not_visited_city_layer.js';
import { ToolbarActions } from './toolbar_actions.js';

function createLayer(markers = new Map()) {
    return {
        markers,
        visible: false,
        clusteringEnabled: true,
        add: vi.fn().mockResolvedValue(),
        show: vi.fn(async function () {
            this.visible = true;
        }),
        hide: vi.fn(async function () {
            this.visible = false;
        }),
        remove: vi.fn(),
        clear: vi.fn(async function () {
            this.visible = false;
        }),
        setClusteringEnabled: vi.fn(async function (enabled) {
            this.clusteringEnabled = enabled;
            return enabled;
        }),
    };
}

function createMap() {
    return {
        addLayer: vi.fn(),
        removeLayer: vi.fn(),
        removeControl: vi.fn(),
        hasLayer: vi.fn(() => false),
    };
}

function deferred() {
    let resolvePromise;
    const promise = new Promise((resolve) => {
        resolvePromise = resolve;
    });
    return { promise, resolve: resolvePromise };
}

function createActions() {
    const actions = Object.create(ToolbarActions.prototype);
    actions.myMap = createMap();
    actions.notVisitedCities = [
        {
            id: 1,
            title: 'Город',
            region: 'Регион',
            region_id: 10,
            country: 'Россия',
            country_code: 'RU',
            lat: 55,
            lon: 37,
        },
    ];
    actions.notVisitedCitiesLoaded = true;
    actions.notVisitedCitiesBuilt = false;
    actions.notVisitedShowPromise = null;
    actions.notVisitedTogglePromise = null;
    actions.notVisitedClusteringTogglePromise = null;
    actions.notVisitedVisibilityListeners = new Set();
    actions.notVisitedLoadControl = null;
    actions.stateOwnCities = new Map();
    actions.stateSubscriptionCities = new Map();
    actions.stateNotVisitedCities = new Map();
    actions.notVisitedCityLayer = createLayer(actions.stateNotVisitedCities);
    actions.elementShowNotVisitedCities = document.createElement('button');
    actions.elementShowNotVisitedCities.dataset.type = 'show';
    actions.elementShowNotVisitedCities.dataset.url = '/api/city/not_visited';
    actions.setButtonState = ToolbarActions.prototype.setButtonState.bind(actions);
    actions.setToggleButtonVariant = vi.fn();
    actions.getUsersWhoVisitedCity = vi.fn(() => new Map());
    actions.finishNotVisitedLoading =
        ToolbarActions.prototype.finishNotVisitedLoading.bind(actions);
    return actions;
}

function createConstructedActions() {
    document.body.innerHTML = `
        <button id="btn_show-subscriptions-cities"></button>
        <button id="btn_show-places"></button>
        <button id="btn_show-not-visited-cities" data-type="show"></button>
        <button id="btn_open_modal_with_subscriptions"></button>
    `;
    const layer = createLayer();
    NotVisitedCityLayer.mockImplementationOnce(() => layer);
    const map = createMap();

    return {
        actions: new ToolbarActions(map, []),
        layer,
        map,
    };
}

describe('ToolbarActions: непосещённые города', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        NotVisitedCityLayer.mockReset();
        vi.spyOn(console, 'error').mockImplementation(() => {});
        document.body.innerHTML = '<select id="id_year_filter"><option value="all" selected>Все годы</option></select>';
        mocks.marker.mockImplementation(() => ({
            addTo: vi.fn(),
            setZIndexOffset: vi.fn(),
        }));
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        vi.restoreAllMocks();
    });

    it('создаёт лёгкие маркеры и передаёт их кластерному слою пакетом', async () => {
        const actions = createActions();

        await actions.addNotVisitedCitiesOnMap();

        expect(actions.notVisitedCityLayer.add).toHaveBeenCalledOnce();
        expect(actions.notVisitedCityLayer.show).toHaveBeenCalledOnce();
        expect(mocks.marker.mock.results[0].value.addTo).not.toHaveBeenCalled();
        expect(actions.getUsersWhoVisitedCity).not.toHaveBeenCalled();
        expect(mocks.bindPopupToMarker).toHaveBeenCalledWith(
            mocks.marker.mock.results[0].value,
            expect.objectContaining({ id: 1, name: 'Город' }),
            expect.objectContaining({
                subscriptionUsers: [],
                lazyPopup: true,
            }),
        );
    });

    it('переиспользует построенный пустой слой без пересборки', async () => {
        const actions = createActions();
        actions.notVisitedCities = [];
        actions.notVisitedCitiesBuilt = true;
        const finishSpy = vi.spyOn(actions, 'finishNotVisitedLoading');

        await actions.addNotVisitedCitiesOnMap();

        expect(mocks.marker).not.toHaveBeenCalled();
        expect(actions.notVisitedCityLayer.add).not.toHaveBeenCalled();
        expect(actions.notVisitedCityLayer.show).toHaveBeenCalledOnce();
        expect(finishSpy).toHaveBeenCalledOnce();
    });

    it('не повторяет API-запрос для уже загруженного пустого списка', async () => {
        const actions = createActions();
        const fetchMock = vi.fn();
        actions.notVisitedCities = [];
        actions.notVisitedCitiesLoaded = true;
        actions.addNotVisitedCitiesOnMap = vi.fn();
        vi.stubGlobal('fetch', fetchMock);

        await actions.showNotVisitedCities();

        expect(fetchMock).not.toHaveBeenCalled();
        expect(actions.addNotVisitedCitiesOnMap).toHaveBeenCalledOnce();
    });

    it('связывает публичный state с индексом созданного слоя', () => {
        const { actions, layer } = createConstructedActions();

        expect(actions.stateNotVisitedCities).toBe(layer.markers);
        expect(actions.notVisitedCitiesBuilt).toBe(false);
    });

    it('сразу сообщает видимость и уведомляет после show, hide и clear', async () => {
        const actions = createActions();
        const listener = vi.fn();

        actions.subscribeNotVisitedVisibility(listener);
        expect(listener).toHaveBeenLastCalledWith(false);

        await actions.addNotVisitedCitiesOnMap();
        expect(listener).toHaveBeenLastCalledWith(true);

        await actions.hideNotVisitedCities();
        expect(listener).toHaveBeenLastCalledWith(false);

        actions.notVisitedCityLayer.visible = true;
        await actions.removeNotVisitedMarkers();
        expect(listener).toHaveBeenLastCalledWith(false);
        expect(listener).toHaveBeenCalledTimes(4);
    });

    it('уведомляет о фактической видимости после ошибки show', async () => {
        const actions = createActions();
        const listener = vi.fn();
        actions.notVisitedCityLayer.show.mockImplementationOnce(function () {
            this.visible = true;
            throw new Error('cluster show failed');
        });

        actions.subscribeNotVisitedVisibility(listener);
        await expect(actions.showNotVisitedCities()).resolves.toBe(false);

        expect(actions.notVisitedCityLayer.visible).toBe(false);
        expect(listener).toHaveBeenLastCalledWith(false);
        expect(listener).toHaveBeenCalledTimes(2);
    });

    it('прекращает уведомления после удаления подписки', async () => {
        const actions = createActions();
        const listener = vi.fn();
        const unsubscribe = actions.subscribeNotVisitedVisibility(listener);

        unsubscribe();
        await actions.addNotVisitedCitiesOnMap();

        expect(listener).toHaveBeenCalledOnce();
        expect(listener).toHaveBeenLastCalledWith(false);
    });

    it('удаляет подписчика, если начальное уведомление завершилось ошибкой', () => {
        const actions = createActions();
        const listenerError = new Error('initial listener failed');
        const listener = vi.fn(() => {
            throw listenerError;
        });

        expect(() => actions.subscribeNotVisitedVisibility(listener)).toThrow(listenerError);

        expect(actions.notVisitedVisibilityListeners.has(listener)).toBe(false);
        expect(listener).toHaveBeenCalledOnce();
    });

    it('не прерывает успешную операцию и уведомляет следующих подписчиков', async () => {
        const actions = createActions();
        const listenerError = new Error('listener failed');
        const throwingListener = vi.fn()
            .mockImplementationOnce(() => {})
            .mockImplementationOnce(() => {
                throw listenerError;
            });
        const laterListener = vi.fn();
        actions.subscribeNotVisitedVisibility(throwingListener);
        actions.subscribeNotVisitedVisibility(laterListener);

        await expect(actions.addNotVisitedCitiesOnMap()).resolves.toBeUndefined();

        expect(laterListener).toHaveBeenLastCalledWith(true);
        expect(console.error).toHaveBeenCalledWith(
            'Ошибка подписчика видимости непосещённых городов:',
            listenerError,
        );
    });

    it('сохраняет исходную ошибку слоя при ошибке подписчика', async () => {
        const actions = createActions();
        const layerError = new Error('cluster show failed');
        const listenerError = new Error('listener failed');
        const listener = vi.fn()
            .mockImplementationOnce(() => {})
            .mockImplementationOnce(() => {
                throw listenerError;
            });
        actions.notVisitedCityLayer.show.mockRejectedValueOnce(layerError);
        actions.subscribeNotVisitedVisibility(listener);

        await expect(actions.addNotVisitedCitiesOnMap()).rejects.toBe(layerError);

        expect(console.error).toHaveBeenCalledWith(
            'Ошибка подписчика видимости непосещённых городов:',
            listenerError,
        );
    });

    it('снимает индикатор только после завершения показа слоя', async () => {
        const { actions, layer, map } = createConstructedActions();
        const loadControl = { id: 'load-control' };
        const showing = deferred();
        actions.notVisitedLoadControl = loadControl;
        actions.notVisitedCitiesBuilt = true;
        layer.show.mockReturnValueOnce(showing.promise);

        const operation = actions.addNotVisitedCitiesOnMap();
        expect(map.removeControl).not.toHaveBeenCalled();

        showing.resolve();
        await operation;
        expect(map.removeControl).toHaveBeenCalledWith(loadControl);
    });

    it('объединяет конкурентные show в один fetch и один load control', async () => {
        const actions = createActions();
        let resolveFetch;
        actions.notVisitedCities = [];
        actions.notVisitedCitiesLoaded = false;
        const fetchMock = vi.fn(() => new Promise((resolve) => {
            resolveFetch = resolve;
        }));
        vi.stubGlobal('fetch', fetchMock);

        const firstShow = actions.showNotVisitedCities();
        const secondShow = actions.showNotVisitedCities();

        expect(secondShow).toBe(firstShow);
        expect(fetchMock).toHaveBeenCalledOnce();
        expect(mocks.addLoadControl).toHaveBeenCalledOnce();

        resolveFetch({ ok: true, json: vi.fn().mockResolvedValue([]) });
        await expect(Promise.all([firstShow, secondShow])).resolves.toEqual([true, true]);
        expect(actions.myMap.removeControl).toHaveBeenCalledOnce();
    });

    it('объединяет конкурентные toggle и обновляет кнопку один раз', async () => {
        const actions = createActions();
        let resolveShow;
        actions.showNotVisitedCities = vi.fn(() => new Promise((resolve) => {
            resolveShow = resolve;
        }));

        const firstToggle = actions.toggleNotVisitedCities();
        const secondToggle = actions.toggleNotVisitedCities();

        expect(secondToggle).toBe(firstToggle);
        expect(actions.showNotVisitedCities).toHaveBeenCalledOnce();

        resolveShow(true);
        await expect(Promise.all([firstToggle, secondToggle])).resolves.toEqual([true, true]);
        expect(actions.elementShowNotVisitedCities.dataset.type).toBe('hide');
        expect(actions.setToggleButtonVariant).toHaveBeenCalledOnce();
    });

    it('переключает кластеризацию только после активного показа', async () => {
        const actions = createActions();
        const activeShow = deferred();
        actions.notVisitedShowPromise = activeShow.promise;

        const toggle = actions.toggleNotVisitedClustering();

        expect(actions.notVisitedCityLayer.setClusteringEnabled).not.toHaveBeenCalled();
        activeShow.resolve(true);
        await expect(toggle).resolves.toBe(false);
        expect(actions.notVisitedCityLayer.setClusteringEnabled).toHaveBeenCalledWith(false);
    });

    it('дедуплицирует параллельные переключения кластеризации', () => {
        const actions = createActions();
        actions.notVisitedCityLayer.setClusteringEnabled.mockImplementation(
            () => new Promise(() => {}),
        );

        expect(actions.toggleNotVisitedClustering()).toBe(
            actions.toggleNotVisitedClustering(),
        );
    });

    it('после ошибки переключения сохраняет режим и разрешает повторную попытку', async () => {
        const actions = createActions();
        const error = new Error('toggle failed');
        actions.notVisitedCityLayer.setClusteringEnabled
            .mockRejectedValueOnce(error)
            .mockImplementationOnce(async (enabled) => {
                actions.notVisitedCityLayer.clusteringEnabled = enabled;
                return enabled;
            });

        await expect(actions.toggleNotVisitedClustering()).resolves.toBe(true);
        await expect(actions.toggleNotVisitedClustering()).resolves.toBe(false);

        expect(actions.notVisitedCityLayer.setClusteringEnabled).toHaveBeenCalledTimes(2);
        expect(mocks.addErrorControl).toHaveBeenCalledWith(
            actions.myMap,
            'Произошла ошибка при переключении кластеризации',
        );
        expect(console.error).toHaveBeenCalledWith(
            'Ошибка при переключении кластеризации:',
            error,
        );
    });

    it('скрывает слой целиком, сохраняя маркеры для повторного показа', () => {
        const actions = createActions();
        actions.stateNotVisitedCities.set(1, { id: 'existing' });

        actions.hideNotVisitedCities();

        expect(actions.notVisitedCityLayer.hide).toHaveBeenCalledOnce();
        expect(actions.notVisitedCityLayer.clear).not.toHaveBeenCalled();
        expect(actions.stateNotVisitedCities.size).toBe(1);
    });

    it('удаляет ставший посещённым город через кластерный слой', () => {
        const actions = createActions();
        const marker = { id: 'existing' };
        actions.notVisitedCityLayer.remove.mockReturnValue(marker);

        expect(actions.removeNotVisitedMarker(1)).toBe(marker);
        expect(actions.notVisitedCityLayer.remove).toHaveBeenCalledWith(1);
    });

    it('оставляет кнопку неактивной после ошибки загрузки', async () => {
        const actions = createActions();
        actions.showNotVisitedCities = vi.fn().mockResolvedValue(false);

        await actions.toggleNotVisitedCities();

        expect(actions.elementShowNotVisitedCities.dataset.type).toBe('show');
        expect(actions.setToggleButtonVariant).toHaveBeenCalledWith(
            actions.elementShowNotVisitedCities,
            'danger',
            false,
        );
    });

    it('переводит кнопку в активное состояние после успешного показа', async () => {
        const actions = createActions();
        actions.notVisitedCities = [];

        await expect(actions.toggleNotVisitedCities()).resolves.toBe(true);

        expect(actions.elementShowNotVisitedCities.dataset.type).toBe('hide');
        expect(actions.setToggleButtonVariant).toHaveBeenCalledWith(
            actions.elementShowNotVisitedCities,
            'danger',
            true,
        );
    });

    it('скрывает слой и переводит активную кнопку в неактивное состояние', async () => {
        const actions = createActions();
        actions.elementShowNotVisitedCities.dataset.type = 'hide';

        await expect(actions.toggleNotVisitedCities()).resolves.toBe(false);

        expect(actions.notVisitedCityLayer.hide).toHaveBeenCalledOnce();
        expect(actions.elementShowNotVisitedCities.dataset.type).toBe('show');
        expect(actions.setToggleButtonVariant).toHaveBeenCalledWith(
            actions.elementShowNotVisitedCities,
            'danger',
            false,
        );
    });

    it('снимает индикатор и показывает ошибку при неуспешном API-запросе', async () => {
        const actions = createActions();
        actions.notVisitedCities = [];
        actions.notVisitedCitiesLoaded = false;
        actions.finishNotVisitedLoading =
            ToolbarActions.prototype.finishNotVisitedLoading.bind(actions);
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }));

        await expect(actions.showNotVisitedCities()).resolves.toBe(false);

        expect(actions.myMap.removeControl).toHaveBeenCalledWith({ id: 'load-control' });
        expect(mocks.addErrorControl).toHaveBeenCalledWith(
            actions.myMap,
            'Произошла ошибка при загрузке непосещённых городов',
        );
    });

    it('пропускает все недопустимые записи и добавляет валидную со строковыми числами', async () => {
        const { actions, layer } = createConstructedActions();
        actions.notVisitedCitiesLoaded = true;
        actions.notVisitedCities = [
            null,
            undefined,
            [],
            { id: true, title: 'Boolean ID', lat: 55, lon: 37 },
            { id: '', title: 'Empty ID', lat: 55, lon: 37 },
            { id: ' ', title: 'Blank ID', lat: 55, lon: 37 },
            { id: NaN, title: 'NaN ID', lat: 55, lon: 37 },
            { id: Infinity, title: 'Infinite ID', lat: 55, lon: 37 },
            { id: 1, title: 'Null latitude', lat: null, lon: 37 },
            { id: 2, title: 'Undefined latitude', lat: undefined, lon: 37 },
            { id: 3, title: 'Boolean latitude', lat: false, lon: 37 },
            { id: 11, title: 'Empty latitude', lat: '', lon: 37 },
            { id: 4, title: 'Blank latitude', lat: '  ', lon: 37 },
            { id: 5, title: 'NaN latitude', lat: NaN, lon: 37 },
            { id: 6, title: 'Infinite longitude', lat: 55, lon: Infinity },
            { id: 7, title: 'Low latitude', lat: -91, lon: 37 },
            { id: 8, title: 'High latitude', lat: 91, lon: 37 },
            { id: 9, title: 'Low longitude', lat: 55, lon: -181 },
            { id: 10, title: 'High longitude', lat: 55, lon: 181 },
            { id: '2', title: 'Валидный', lat: '59.93', lon: '30.31' },
        ];

        const showPromise = actions.showNotVisitedCities();

        await expect(showPromise).resolves.toBe(true);
        expect(layer.add).toHaveBeenCalledWith([
            expect.objectContaining({ cityId: 2, marker: mocks.marker.mock.results[0].value }),
        ]);
        expect(mocks.marker).toHaveBeenCalledWith(
            [59.93, 30.31],
            expect.any(Object),
        );
        expect(layer.show).toHaveBeenCalledOnce();
        expect(console.error).toHaveBeenCalledTimes(19);
        expect(console.error.mock.calls.map((call) => call[1])).toEqual([
            undefined, undefined, undefined, true, '', ' ', NaN, Infinity,
            1, 2, 3, 11, 4, 5, 6, 7, 8, 9, 10,
        ]);
        expect(console.error.mock.calls.every((call) => (
            call[0] === 'Ошибка при создании маркера непосещённого города:' &&
            call[2] instanceof Error
        ))).toBe(true);
        expect(mocks.addErrorControl).not.toHaveBeenCalled();
    });

    it('после ошибки add очищает слой и успешно строит его повторно', async () => {
        const { actions, layer } = createConstructedActions();
        const addError = new Error('cluster add failed');
        actions.notVisitedCitiesLoaded = true;
        actions.notVisitedCities = [{ id: 1, title: 'Город', lat: 55, lon: 37 }];
        layer.add
            .mockImplementationOnce((entries) => {
                entries.forEach(({ cityId, marker }) => layer.markers.set(cityId, marker));
                throw addError;
            })
            .mockImplementationOnce((entries) => {
                entries.forEach(({ cityId, marker }) => layer.markers.set(cityId, marker));
            });
        layer.clear.mockImplementation(() => layer.markers.clear());

        await expect(actions.showNotVisitedCities()).resolves.toBe(false);
        expect(actions.notVisitedCitiesBuilt).toBe(false);
        expect(layer.hide).toHaveBeenCalledOnce();
        expect(layer.clear).toHaveBeenCalledOnce();
        expect(layer.markers.size).toBe(0);
        expect(console.error).toHaveBeenCalledWith('Ошибка при выполнении запроса:', addError);

        const retryPromise = actions.showNotVisitedCities();

        await expect(retryPromise).resolves.toBe(true);
        expect(layer.add).toHaveBeenCalledTimes(2);
        expect(layer.show).toHaveBeenCalledOnce();
        expect(layer.markers.has(1)).toBe(true);
        expect(actions.notVisitedCitiesBuilt).toBe(true);
    });

    it('после частичной регистрации и ошибки show очищает слой и успешно строит его повторно', async () => {
        const { actions, layer, map } = createConstructedActions();
        const showError = new Error('cluster show failed');
        actions.notVisitedCitiesLoaded = true;
        actions.notVisitedCities = [{ id: 1, title: 'Город', lat: 55, lon: 37 }];
        layer.add.mockImplementation((entries) => {
            entries.forEach(({ cityId, marker }) => layer.markers.set(cityId, marker));
        });
        layer.show
            .mockImplementationOnce(() => {
                map.hasLayer.mockReturnValue(true);
                throw showError;
            })
            .mockImplementationOnce(() => {
                map.hasLayer.mockReturnValue(true);
            });
        layer.hide.mockImplementation(() => {
            if (map.hasLayer(layer)) {
                map.removeLayer(layer);
                map.hasLayer.mockReturnValue(false);
            }
        });
        layer.clear.mockImplementation(() => layer.markers.clear());

        await expect(actions.showNotVisitedCities()).resolves.toBe(false);
        expect(map.removeLayer).toHaveBeenCalledWith(layer);
        expect(layer.markers.size).toBe(0);
        expect(actions.notVisitedCitiesBuilt).toBe(false);

        const retryPromise = actions.showNotVisitedCities();

        await expect(retryPromise).resolves.toBe(true);
        expect(layer.add).toHaveBeenCalledTimes(2);
        expect(layer.show).toHaveBeenCalledTimes(2);
        expect(layer.markers.has(1)).toBe(true);
        expect(actions.notVisitedCitiesBuilt).toBe(true);
    });

    it('после ошибки повторного show сбрасывает cached built-state и перестраивает слой', async () => {
        const { actions, layer } = createConstructedActions();
        const showError = new Error('cached cluster show failed');
        actions.notVisitedCitiesLoaded = true;
        actions.notVisitedCitiesBuilt = true;
        actions.notVisitedCities = [{ id: 1, title: 'Город', lat: 55, lon: 37 }];
        layer.show.mockImplementationOnce(() => {
            throw showError;
        });

        await expect(actions.showNotVisitedCities()).resolves.toBe(false);
        expect(actions.notVisitedCitiesBuilt).toBe(false);
        expect(layer.hide).toHaveBeenCalledOnce();
        expect(layer.clear).toHaveBeenCalledOnce();

        const retryPromise = actions.showNotVisitedCities();

        await expect(retryPromise).resolves.toBe(true);
        expect(layer.add).toHaveBeenCalledOnce();
        expect(layer.show).toHaveBeenCalledTimes(2);
        expect(actions.notVisitedCitiesBuilt).toBe(true);
    });

    it('не маскирует исходную ошибку show ошибкой cleanup и продолжает очистку', async () => {
        const actions = createActions();
        const showError = new Error('cluster show failed');
        const hideError = new Error('cluster hide failed');
        actions.notVisitedCityLayer.show.mockImplementationOnce(() => {
            throw showError;
        });
        actions.notVisitedCityLayer.hide.mockImplementationOnce(() => {
            throw hideError;
        });

        await expect(actions.showNotVisitedCities()).resolves.toBe(false);

        expect(actions.notVisitedCityLayer.clear).toHaveBeenCalledOnce();
        expect(console.error).toHaveBeenCalledWith(
            'Ошибка при очистке слоя непосещённых городов:',
            hideError,
        );
        expect(console.error).toHaveBeenCalledWith('Ошибка при выполнении запроса:', showError);
    });

    it.each([
        ['добавлении к кластеру', (actions) => {
            actions.notVisitedCityLayer.add.mockImplementationOnce(() => {
                throw new Error('cluster add failed');
            });
        }],
        ['показе кластера', (actions) => {
            actions.notVisitedCityLayer.show.mockImplementationOnce(() => {
                throw new Error('cluster show failed');
            });
        }],
    ])('очищает загрузку и возвращает false при ошибке на %s', async (stage, fail) => {
        const actions = createActions();
        fail(actions);

        await expect(actions.showNotVisitedCities()).resolves.toBe(false);

        expect(actions.myMap.removeControl).toHaveBeenCalledWith({ id: 'load-control' });
        expect(mocks.addErrorControl).toHaveBeenCalledWith(
            actions.myMap,
            'Произошла ошибка при загрузке непосещённых городов',
        );
    });

    it('полная очистка сбрасывает built-state и разрешает повторную сборку', async () => {
        const actions = createActions();
        actions.notVisitedCities = [];
        actions.notVisitedCitiesBuilt = true;

        await actions.removeNotVisitedMarkers();
        await actions.addNotVisitedCitiesOnMap();

        expect(actions.notVisitedCityLayer.clear).toHaveBeenCalledOnce();
        expect(actions.notVisitedCityLayer.add).toHaveBeenCalledOnce();
        expect(actions.notVisitedCitiesBuilt).toBe(true);
    });

    it('полная очистка ждёт ожидающую fetch-операцию перед clear', async () => {
        const actions = createActions();
        let resolveFetch;
        actions.notVisitedCitiesLoaded = false;
        vi.stubGlobal('fetch', vi.fn(() => new Promise((resolve) => {
            resolveFetch = resolve;
        })));
        const showPromise = actions.showNotVisitedCities();

        const clearPromise = actions.removeNotVisitedMarkers();
        expect(actions.notVisitedCityLayer.clear).not.toHaveBeenCalled();
        resolveFetch({ ok: true, json: vi.fn().mockResolvedValue([]) });

        await expect(showPromise).resolves.toBe(true);
        await clearPromise;
        expect(actions.notVisitedCityLayer.clear).toHaveBeenCalledOnce();
        expect(actions.notVisitedCitiesBuilt).toBe(false);
    });

    it('сбрасывает built-state при ошибке полной очистки', async () => {
        const actions = createActions();
        const clearError = new Error('clear failed');
        actions.notVisitedCitiesBuilt = true;
        actions.stateNotVisitedCities.set(1, { id: 'stale' });
        actions.notVisitedCityLayer.clear.mockImplementationOnce(async () => {
            actions.stateNotVisitedCities.clear();
            throw clearError;
        });

        await expect(actions.removeNotVisitedMarkers()).rejects.toBe(clearError);

        expect(actions.notVisitedCitiesBuilt).toBe(false);
        await actions.addNotVisitedCitiesOnMap();
        expect(actions.notVisitedCityLayer.add).toHaveBeenCalledOnce();
        expect(actions.notVisitedCityLayer.show).toHaveBeenCalledOnce();
        expect(actions.notVisitedCitiesBuilt).toBe(true);
    });

    it('не начинает повторную сборку до завершения старого show', async () => {
        const { actions, layer, map } = createConstructedActions();
        const order = [];
        const showing = deferred();
        actions.notVisitedCitiesLoaded = true;
        actions.notVisitedCities = [{ id: 1, title: 'Город', lat: 55, lon: 37 }];
        layer.add.mockImplementation(async () => order.push('add'));
        layer.show
            .mockImplementationOnce(() => showing.promise)
            .mockResolvedValueOnce();
        layer.clear.mockImplementation(async () => order.push('clear'));

        const oldShowPromise = actions.showNotVisitedCities();
        let resyncSettled = false;
        const resyncPromise = Promise.resolve(actions.removeNotVisitedMarkers())
            .then(() => actions.addNotVisitedCitiesOnMap())
            .then(() => {
                resyncSettled = true;
            });

        await vi.waitFor(() => expect(order).toEqual(['add']));
        expect(layer.clear).not.toHaveBeenCalled();

        showing.resolve();
        await oldShowPromise;
        await vi.waitFor(() => expect(layer.add).toHaveBeenCalledTimes(2));

        expect(order).toEqual(['add', 'clear', 'add']);
        expect(resyncSettled).toBe(true);
        expect(map.removeControl).toHaveBeenCalledTimes(1);
        await resyncPromise;
        expect(map.removeControl).toHaveBeenCalledTimes(1);
    });

    it('showSubscriptionCities ждёт clear и rebuild перед включением Apply', async () => {
        const actions = createActions();
        const clear = deferred();
        const rebuild = deferred();
        document.body.insertAdjacentHTML(
            'beforeend',
            '<button id="btn_show-subscriptions-cities" data-url="/api/subscriptions"></button>',
        );
        const applyButton = document.getElementById('btn_show-subscriptions-cities');
        actions.elementShowSubscriptionCities = applyButton;
        actions.elementOpenSubscriptionsModal = document.createElement('button');
        actions.elementShowNotVisitedCities.dataset.type = 'hide';
        actions.removeOwnMarkers = vi.fn();
        actions.removeSubscriptionMarkers = vi.fn();
        actions.removeNotVisitedMarkers = vi.fn(() => clear.promise);
        actions.addOwnCitiesOnMap = vi.fn();
        actions.addSubscriptionsCitiesOnMap = vi.fn();
        actions.addNotVisitedCitiesOnMap = vi.fn(() => rebuild.promise);
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([{ id: 2, username: 'new-user' }]),
        }));

        const subscriptionPromise = actions.showSubscriptionCities();
        await vi.waitFor(() => expect(actions.removeNotVisitedMarkers).toHaveBeenCalledOnce());

        expect(actions.addOwnCitiesOnMap).not.toHaveBeenCalled();
        expect(actions.addNotVisitedCitiesOnMap).not.toHaveBeenCalled();
        expect(applyButton.disabled).toBe(true);

        clear.resolve();
        await vi.waitFor(() => expect(actions.addNotVisitedCitiesOnMap).toHaveBeenCalledOnce());

        expect(actions.subscriptionCities).toEqual([{ id: 2, username: 'new-user' }]);
        expect(actions.addOwnCitiesOnMap).toHaveBeenCalledOnce();
        expect(actions.addSubscriptionsCitiesOnMap).toHaveBeenCalledOnce();
        expect(applyButton.disabled).toBe(true);

        rebuild.resolve();
        await subscriptionPromise;
        expect(applyButton.disabled).toBe(false);
        expect(applyButton.innerText).toBe('Применить');
    });

    it.each([
        ['очистки', (actions, error) => {
            actions.removeNotVisitedMarkers = vi.fn().mockRejectedValue(error);
            actions.addNotVisitedCitiesOnMap = vi.fn();
        }],
        ['перестроения', (actions, error) => {
            actions.removeNotVisitedMarkers = vi.fn().mockResolvedValue();
            actions.addNotVisitedCitiesOnMap = vi.fn().mockRejectedValue(error);
        }],
    ])('восстанавливает Apply и показывает ошибку при отказе %s', async (stage, fail) => {
        const actions = createActions();
        const error = new Error(`${stage} failed`);
        document.body.insertAdjacentHTML(
            'beforeend',
            '<button id="btn_show-subscriptions-cities" data-url="/api/subscriptions"></button>',
        );
        const applyButton = document.getElementById('btn_show-subscriptions-cities');
        actions.elementShowSubscriptionCities = applyButton;
        actions.elementOpenSubscriptionsModal = document.createElement('button');
        actions.elementShowNotVisitedCities.dataset.type = 'hide';
        actions.removeOwnMarkers = vi.fn();
        actions.removeSubscriptionMarkers = vi.fn();
        actions.addOwnCitiesOnMap = vi.fn();
        actions.addSubscriptionsCitiesOnMap = vi.fn();
        fail(actions, error);
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([{ id: 2, username: 'new-user' }]),
        }));

        await expect(actions.showSubscriptionCities()).resolves.toBe(false);

        expect(applyButton.disabled).toBe(false);
        expect(applyButton.innerText).toBe('Применить');
        expect(console.error).toHaveBeenCalledWith(
            'Ошибка при загрузке городов подписок:',
            error,
        );
        expect(mocks.addErrorControl).toHaveBeenCalledWith(
            actions.myMap,
            'Произошла ошибка при загрузке городов подписок',
        );
    });

    it('сохраняет validation toast и восстанавливает Apply для non-OK ответа', async () => {
        const actions = createActions();
        const showToast = vi.fn();
        document.body.insertAdjacentHTML(
            'beforeend',
            '<button id="btn_show-subscriptions-cities" data-url="/api/subscriptions"></button><div id="toast_validation_error"></div>',
        );
        const applyButton = document.getElementById('btn_show-subscriptions-cities');
        actions.elementShowSubscriptionCities = applyButton;
        vi.stubGlobal('bootstrap', {
            Toast: vi.fn(() => ({ show: showToast })),
        });
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }));

        await expect(actions.showSubscriptionCities()).resolves.toBe(false);

        expect(showToast).toHaveBeenCalledOnce();
        expect(mocks.addErrorControl).not.toHaveBeenCalled();
        expect(applyButton.disabled).toBe(false);
        expect(applyButton.innerText).toBe('Применить');
    });

    it('updateMarker удаляет кластерный маркер через слой', () => {
        const actions = createActions();
        const city = { id: 1, lat: 55, lon: 37 };
        actions.stateNotVisitedCities.set(city.id, { id: 'clustered' });

        actions.updateMarker(city);

        expect(actions.notVisitedCityLayer.remove).toHaveBeenCalledWith(city.id);
        expect(actions.stateOwnCities.get(city.id)).toBe(mocks.marker.mock.results[0].value);
        expect(actions.myMap.removeLayer).not.toHaveBeenCalled();
    });

    it('обычный маркер без options добавляется напрямую и получает не ленивый popup', () => {
        const actions = createActions();
        const city = { id: 1, name: 'Город', lat: 55, lon: 37 };

        const marker = actions.addMarkerToMap(city, 'own', []);

        expect(marker.addTo).toHaveBeenCalledWith(actions.myMap);
        expect(mocks.bindPopupToMarker).toHaveBeenCalledWith(
            marker,
            expect.objectContaining({ id: city.id }),
            expect.objectContaining({ lazyPopup: false }),
        );
    });

    it('map_city делегирует удаление кластерного маркера ToolbarActions', () => {
        const source = readFileSync(
            resolve(process.cwd(), 'js/entries/map_city.js'),
            'utf8',
        );

        expect(source).toMatch(/if \(city\?\.id && actions\) \{\s*actions\.removeNotVisitedMarker\(city\.id\);\s*\}/);
        expect(source).not.toContain('stateNotVisitedCities.delete');
    });

    it('map_city подключает контрол кластеризации к ToolbarActions', () => {
        const source = readFileSync(
            resolve(process.cwd(), 'js/entries/map_city.js'),
            'utf8',
        );

        expect(source).toMatch(
            /import \{\s*addNotVisitedClusteringControl,\s*syncNotVisitedClusteringControl,\s*\} from '\.\.\/components\/not_visited_clustering_control\.js';/,
        );
        expect(source).toMatch(
            /actions = new ToolbarActions\(map, own_cities\);\s*const clusteringControl = addNotVisitedClusteringControl\(map, \{\s*getEnabled: \(\) => actions\.isNotVisitedClusteringEnabled\(\),\s*getVisible: \(\) => actions\.isNotVisitedCitiesVisible\(\),\s*onToggle: \(\) => actions\.toggleNotVisitedClustering\(\),\s*\}\);\s*actions\.subscribeNotVisitedVisibility\(\(\) => \{\s*syncNotVisitedClusteringControl\(clusteringControl\);\s*\}\);/,
        );
    });
});
