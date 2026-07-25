<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Unvisited City Marker Clustering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Устранить зависания основной карты при показе более тысячи непосещённых городов с помощью пакетной кластеризации и ленивой подготовки popup.

**Architecture:** Отдельный `NotVisitedCityLayer` инкапсулирует `L.MarkerClusterGroup`, индекс маркеров и операции показа, скрытия и удаления. `ToolbarActions` остаётся владельцем бизнес-сценария загрузки городов, но создаёт лёгкие маркеры без прямого добавления на карту и передаёт их кластерному слою одним пакетом; popup непосещённого города строится только при первом открытии.

**Tech Stack:** JavaScript, Leaflet 1.9.4, Leaflet.markercluster 1.5.3, Vitest 2.1, happy-dom 20, Vite 5.4.

## Global Constraints

- Изменение применяется только к основной карте `map_city`; другие карты не переводятся на кластерное поведение.
- Текущий API непосещённых городов и его формат ответа не меняются.
- Посещённые города, города подписок и места остаются обычными Leaflet-маркерами.
- Непосещённые маркеры добавляются через `MarkerClusterGroup.addLayers()` с `chunkedLoading: true`.
- Кластеризация непосещённых маркеров отключается на zoom `8` и выше через `disableClusteringAtZoom: 8`.
- `stateNotVisitedCities` сохраняет интерфейс `Map<cityId, marker>` для существующих потребителей.
- Повторный показ не выполняет новый API-запрос и не пересоздаёт маркеры.
- Popup непосещённого города строится лениво и кешируется после первого построения.
- Не добавлять серверную загрузку по viewport и не менять картографический движок.
- Не создавать тесты, проверяющие только CSS-классы или внешний вид кластеров.
- Каждый изменяемый и создаваемый файл должен содержать лицензионный блок проекта.
- Не создавать коммит без новой прямой команды пользователя.

---

### Task 1: Изолированный кластерный слой непосещённых городов

**Files:**
- Modify: `frontend/package.json:18-27`
- Modify: `frontend/package-lock.json`
- Create: `frontend/js/components/not_visited_city_layer.js`
- Create: `frontend/js/components/not_visited_city_layer.test.js`

**Interfaces:**
- Consumes: `L.markerClusterGroup(options)`, объект карты с `addLayer`, `removeLayer`, `hasLayer`.
- Produces: класс `NotVisitedCityLayer`; свойства `markers: Map<number, L.Marker>` и `clusterGroup: L.MarkerClusterGroup`; методы `add(entries)`, `show()`, `hide()`, `remove(cityId)`, `clear()`.
- `entries` имеет форму `Array<{cityId: number, marker: L.Marker}>`.

- [ ] **Step 1: Установить точную версию Leaflet.markercluster**

Run:

```bash
npm --prefix frontend install leaflet.markercluster@1.5.3
```

Expected: `frontend/package.json` содержит `"leaflet.markercluster": "^1.5.3"`, lock-файл содержит пакет версии `1.5.3`, `npm` завершается с кодом `0`.

- [ ] **Step 2: Написать падающие unit-тесты кластерного слоя**

Создать `frontend/js/components/not_visited_city_layer.test.js`:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
    markerClusterGroup: vi.fn(),
}));

vi.mock('leaflet', () => ({
    default: {
        markerClusterGroup: mocks.markerClusterGroup,
    },
}));

vi.mock('leaflet.markercluster', () => ({}));

import { NotVisitedCityLayer } from './not_visited_city_layer.js';

describe('NotVisitedCityLayer', () => {
    let clusterGroup;
    let map;

    beforeEach(() => {
        clusterGroup = {
            addLayers: vi.fn(),
            clearLayers: vi.fn(),
            removeLayer: vi.fn(),
        };
        map = {
            addLayer: vi.fn(),
            removeLayer: vi.fn(),
            hasLayer: vi.fn(() => false),
        };
        mocks.markerClusterGroup.mockReset();
        mocks.markerClusterGroup.mockReturnValue(clusterGroup);
    });

    it('создаёт кластер с пакетной загрузкой и передаёт прогресс наружу', () => {
        const onChunkProgress = vi.fn();
        new NotVisitedCityLayer(map, { onChunkProgress });

        expect(mocks.markerClusterGroup).toHaveBeenCalledWith({
            chunkedLoading: true,
            chunkProgress: onChunkProgress,
            removeOutsideVisibleBounds: true,
        });
    });

    it('добавляет новые маркеры одним пакетом и индексирует их по ID', () => {
        const layer = new NotVisitedCityLayer(map);
        const firstMarker = { id: 'first' };
        const secondMarker = { id: 'second' };

        layer.add([
            { cityId: 1, marker: firstMarker },
            { cityId: 2, marker: secondMarker },
        ]);

        expect(clusterGroup.addLayers).toHaveBeenCalledOnce();
        expect(clusterGroup.addLayers).toHaveBeenCalledWith([firstMarker, secondMarker]);
        expect(layer.markers.get(1)).toBe(firstMarker);
        expect(layer.markers.get(2)).toBe(secondMarker);
    });

    it('не добавляет повторно уже проиндексированный город', () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };

        layer.add([{ cityId: 1, marker }]);
        layer.add([{ cityId: 1, marker: { id: 'duplicate' } }]);

        expect(clusterGroup.addLayers).toHaveBeenCalledTimes(1);
        expect(layer.markers.get(1)).toBe(marker);
    });

    it('показывает и скрывает весь слой без удаления маркеров', () => {
        const layer = new NotVisitedCityLayer(map);

        layer.show();
        expect(map.addLayer).toHaveBeenCalledWith(clusterGroup);

        map.hasLayer.mockReturnValue(true);
        layer.hide();
        expect(map.removeLayer).toHaveBeenCalledWith(clusterGroup);
        expect(clusterGroup.clearLayers).not.toHaveBeenCalled();
    });

    it('удаляет один город из кластера и индекса', () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };
        layer.add([{ cityId: 1, marker }]);

        expect(layer.remove(1)).toBe(marker);
        expect(clusterGroup.removeLayer).toHaveBeenCalledWith(marker);
        expect(layer.markers.has(1)).toBe(false);
        expect(layer.remove(999)).toBeNull();
    });

    it('полностью очищает кластер при синхронизации данных', () => {
        const layer = new NotVisitedCityLayer(map);
        layer.add([{ cityId: 1, marker: { id: 'first' } }]);

        layer.clear();

        expect(clusterGroup.clearLayers).toHaveBeenCalledOnce();
        expect(layer.markers.size).toBe(0);
    });
});
```

- [ ] **Step 3: Запустить тест и убедиться, что он падает из-за отсутствующего модуля**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js
```

Expected: FAIL с ошибкой разрешения `./not_visited_city_layer.js`.

- [ ] **Step 4: Реализовать кластерный слой**

Создать `frontend/js/components/not_visited_city_layer.js`:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import L from 'leaflet';
import 'leaflet.markercluster';

export class NotVisitedCityLayer {
    constructor(map, { onChunkProgress = undefined } = {}) {
        this.map = map;
        this.markers = new Map();
        this.clusterGroup = L.markerClusterGroup({
            chunkedLoading: true,
            chunkProgress: onChunkProgress,
            removeOutsideVisibleBounds: true,
        });
    }

    add(entries) {
        const markersToAdd = [];

        entries.forEach(({ cityId, marker }) => {
            if (this.markers.has(cityId)) {
                return;
            }
            this.markers.set(cityId, marker);
            markersToAdd.push(marker);
        });

        if (markersToAdd.length > 0) {
            this.clusterGroup.addLayers(markersToAdd);
        }
    }

    show() {
        if (!this.map.hasLayer(this.clusterGroup)) {
            this.map.addLayer(this.clusterGroup);
        }
    }

    hide() {
        if (this.map.hasLayer(this.clusterGroup)) {
            this.map.removeLayer(this.clusterGroup);
        }
    }

    remove(cityId) {
        const marker = this.markers.get(cityId);
        if (!marker) {
            return null;
        }

        this.clusterGroup.removeLayer(marker);
        this.markers.delete(cityId);
        return marker;
    }

    clear() {
        this.clusterGroup.clearLayers();
        this.markers.clear();
    }
}
```

- [ ] **Step 5: Запустить unit-тест кластерного слоя**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js
```

Expected: PASS, 6 tests passed.

- [ ] **Step 6: Проверить изменения задачи без коммита**

Run:

```bash
git diff --check -- frontend/package.json frontend/package-lock.json frontend/js/components/not_visited_city_layer.js frontend/js/components/not_visited_city_layer.test.js
```

Expected: код возврата `0`, вывода нет, коммит не создан.

---

### Task 2: Ленивая и кешируемая подготовка popup

**Files:**
- Create: `frontend/js/components/city_popup.test.js`
- Modify: `frontend/js/components/city_popup.js:273-291`

**Interfaces:**
- Consumes: текущие `buildPopupContent(cityData, options)` и `bindPopupToLayer(layer, cityData, options)`.
- Produces: дополнительная опция `lazyPopup: boolean` для `bindPopupToLayer` и `bindPopupToMarker`; при `true` в `layer.bindPopup` передаётся функция с кешированием результата.
- Значение по умолчанию `lazyPopup: false` сохраняет поведение всех существующих карт.

- [ ] **Step 1: Написать падающие тесты ленивого popup**

Создать `frontend/js/components/city_popup.test.js`:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { describe, expect, it, vi } from 'vitest';

class Path {}

vi.mock('leaflet', () => ({
    default: { Path },
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

        bindPopupToLayer(layer, cityData, {
            isAuthenticated: true,
            lazyPopup: true,
        });

        const contentFactory = layer.bindPopup.mock.calls[0][0];
        expect(contentFactory).toEqual(expect.any(Function));
        const firstContent = contentFactory();
        const secondContent = contentFactory();
        expect(firstContent).toContain('Тестовый город');
        expect(secondContent).toBe(firstContent);
    });
});
```

- [ ] **Step 2: Запустить тест и зафиксировать правильное падение**

Run:

```bash
npm --prefix frontend test -- js/components/city_popup.test.js
```

Expected: первый тест PASS, второй FAIL, потому что `bindPopup` получает строку вместо функции.

- [ ] **Step 3: Добавить опцию ленивого построения без изменения поведения по умолчанию**

В `bindPopupToLayer` отделить служебную опцию от параметров содержимого и выбирать строку либо кеширующую функцию:

```javascript
export const bindPopupToLayer = (layer, cityData, options = {}) => {
    const { lazyPopup = false, ...popupOptions } = options;
    let cachedPopupContent;
    const getPopupContent = () => {
        if (cachedPopupContent === undefined) {
            cachedPopupContent = buildPopupContent(cityData, popupOptions);
        }
        return cachedPopupContent;
    };

    layer.bindPopup(
        lazyPopup ? getPopupContent : getPopupContent(),
        { maxWidth: 400, minWidth: 280 },
    );
    layer.on('popupopen', () => {
        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
            window.HSStaticMethods.autoInit();
        }
    });
    const tooltipOptions = { direction: 'top' };
    if (layer instanceof L.Path) {
        tooltipOptions.sticky = true;
    }
    layer.bindTooltip(cityData.name, tooltipOptions);
    layer.on('mouseover', function () {
        const tooltip = this.getTooltip();
        if (!tooltip) {
            return;
        }
        if (this.isPopupOpen()) {
            tooltip.setOpacity(0.0);
        } else {
            tooltip.setOpacity(0.9);
        }
    });
    layer.on('click', function () {
        const tooltip = this.getTooltip();
        if (tooltip) {
            tooltip.setOpacity(0.0);
        }
    });
};
```

- [ ] **Step 4: Запустить тесты popup**

Run:

```bash
npm --prefix frontend test -- js/components/city_popup.test.js
```

Expected: PASS, 2 tests passed.

- [ ] **Step 5: Проверить изменения задачи без коммита**

Run:

```bash
git diff --check -- frontend/js/components/city_popup.js frontend/js/components/city_popup.test.js
```

Expected: код возврата `0`, вывода нет, коммит не создан.

---

### Task 3: Интеграция кластерного слоя с ToolbarActions

**Files:**
- Create: `frontend/js/components/toolbar_actions.test.js`
- Modify: `frontend/js/components/toolbar_actions.js:1-12,32-44,54-85,202-235,272-275,387-456,505-517,579-583`
- Modify: `frontend/js/entries/map_city.js:77-86`

**Interfaces:**
- Consumes: `NotVisitedCityLayer`, `bindPopupToMarker(..., { lazyPopup: true })`, текущий API из `data-url` кнопки.
- Produces: `ToolbarActions.removeNotVisitedMarker(cityId): L.Marker | null`, `ToolbarActions.toggleNotVisitedCities(): Promise<boolean>`, расширенная сигнатура `addMarkerToMap(city, markerStyle, users, { addToMap?: boolean, lazyPopup?: boolean } = {})`.
- `stateNotVisitedCities` становится ссылкой на `notVisitedCityLayer.markers`, поэтому существующий интерфейс `Map` сохраняется.

- [ ] **Step 1: Написать тесты интеграции ToolbarActions с кластерным слоем**

Создать `frontend/js/components/toolbar_actions.test.js` со всеми импортами замоканными до динамического импорта:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { beforeEach, describe, expect, it, vi } from 'vitest';

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

import { ToolbarActions } from './toolbar_actions.js';

function createActions() {
    const actions = Object.create(ToolbarActions.prototype);
    actions.myMap = {
        addLayer: vi.fn(),
        removeLayer: vi.fn(),
        removeControl: vi.fn(),
        hasLayer: vi.fn(() => false),
    };
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
    actions.stateOwnCities = new Map();
    actions.stateSubscriptionCities = new Map();
    actions.stateNotVisitedCities = new Map();
    actions.notVisitedCityLayer = {
        markers: actions.stateNotVisitedCities,
        add: vi.fn(({ length }) => length),
        show: vi.fn(),
        hide: vi.fn(),
        remove: vi.fn(),
        clear: vi.fn(),
    };
    actions.elementShowNotVisitedCities = document.createElement('button');
    actions.elementShowNotVisitedCities.dataset.type = 'show';
    actions.elementShowNotVisitedCities.dataset.url = '/api/city/not_visited';
    actions.setButtonState = ToolbarActions.prototype.setButtonState.bind(actions);
    actions.setToggleButtonVariant = vi.fn();
    actions.getUsersWhoVisitedCity = vi.fn(() => new Map());
    actions.finishNotVisitedLoading = vi.fn();
    return actions;
}

describe('ToolbarActions: непосещённые города', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = '<select id="id_year_filter"><option value="all" selected>Все годы</option></select>';
        mocks.marker.mockImplementation(() => ({
            addTo: vi.fn(),
            setZIndexOffset: vi.fn(),
        }));
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('создаёт лёгкие маркеры и передаёт их кластерному слою пакетом', () => {
        const actions = createActions();

        actions.addNotVisitedCitiesOnMap();

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

    it('при повторном показе использует готовый слой и не создаёт маркеры', () => {
        const actions = createActions();
        actions.stateNotVisitedCities.set(1, { id: 'existing' });

        actions.addNotVisitedCitiesOnMap();

        expect(mocks.marker).not.toHaveBeenCalled();
        expect(actions.notVisitedCityLayer.add).not.toHaveBeenCalled();
        expect(actions.notVisitedCityLayer.show).toHaveBeenCalledOnce();
        expect(actions.finishNotVisitedLoading).toHaveBeenCalledOnce();
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
});
```

- [ ] **Step 2: Запустить тест и убедиться, что отсутствуют новые интерфейсы**

Run:

```bash
npm --prefix frontend test -- js/components/toolbar_actions.test.js
```

Expected: FAIL из-за отсутствия кластерной интеграции, `toggleNotVisitedCities` и `removeNotVisitedMarker`.

- [ ] **Step 3: Подключить кластерный слой и сохранить интерфейс состояния**

В начало `toolbar_actions.js` добавить лицензионный блок перед импортами, явный импорт Leaflet и новый компонент:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import L from 'leaflet';
import { NotVisitedCityLayer } from './not_visited_city_layer.js';
```

В конструкторе заменить самостоятельное создание `stateNotVisitedCities`:

```javascript
this.notVisitedLoadControl = null;
this.notVisitedCitiesLoaded = false;
this.notVisitedCityLayer = new NotVisitedCityLayer(this.myMap, {
    onChunkProgress: (processed, total) => {
        if (processed === total) {
            this.finishNotVisitedLoading();
        }
    },
});
this.stateNotVisitedCities = this.notVisitedCityLayer.markers;
```

- [ ] **Step 4: Сделать переключение кнопки зависимым от результата загрузки**

В `set_handlers()` заменить обработчик кнопки:

```javascript
this.elementShowNotVisitedCities.addEventListener('click', () => {
    void this.toggleNotVisitedCities();
});
```

Добавить метод:

```javascript
async toggleNotVisitedCities() {
    if (this.elementShowNotVisitedCities.dataset.type === 'show') {
        const isVisible = await this.showNotVisitedCities();
        this.setButtonState(this.elementShowNotVisitedCities, isVisible);
        this.setToggleButtonVariant(
            this.elementShowNotVisitedCities,
            'danger',
            isVisible,
        );
        return isVisible;
    }

    this.hideNotVisitedCities();
    this.setButtonState(this.elementShowNotVisitedCities, false);
    this.setToggleButtonVariant(this.elementShowNotVisitedCities, 'danger', false);
    return false;
}
```

Изменить `showNotVisitedCities()` так, чтобы он сохранял контрол, возвращал boolean и не снимал индикатор до завершения chunk processing:

```javascript
async showNotVisitedCities() {
    this.notVisitedLoadControl = addLoadControl(
        this.myMap,
        'Загружаю непосещённые города...',
    );

    if (!this.notVisitedCitiesLoaded) {
        try {
            const response = await fetch(this.elementShowNotVisitedCities.dataset.url, {
                method: 'GET',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.notVisitedCities = await response.json();
            this.notVisitedCitiesLoaded = true;
        } catch (error) {
            console.error('Ошибка при выполнении запроса:', error);
            this.finishNotVisitedLoading();
            addErrorControl(
                this.myMap,
                'Произошла ошибка при загрузке непосещённых городов',
            );
            return false;
        }
    }

    this.addNotVisitedCitiesOnMap();
    return true;
}

finishNotVisitedLoading() {
    if (!this.notVisitedLoadControl) {
        return;
    }
    this.myMap.removeControl(this.notVisitedLoadControl);
    this.notVisitedLoadControl = null;
}
```

- [ ] **Step 5: Создавать маркеры без прямого добавления на карту и без расчёта пользователей**

Заменить `addNotVisitedCitiesOnMap()`:

```javascript
addNotVisitedCitiesOnMap() {
    if (this.stateNotVisitedCities.size > 0) {
        this.notVisitedCityLayer.show();
        this.finishNotVisitedLoading();
        return;
    }

    const entries = [];
    for (const cityData of this.notVisitedCities) {
        if (
            this.stateOwnCities.has(cityData.id) ||
            this.stateSubscriptionCities.has(cityData.id)
        ) {
            continue;
        }

        const city = new City();
        city.id = cityData.id;
        city.name = cityData.title;
        city.region = cityData.region;
        city.region_id = cityData.region_id;
        city.country = cityData.country;
        city.country_code = cityData.country_code;
        city.lat = cityData.lat;
        city.lon = cityData.lon;

        try {
            const marker = this.addMarkerToMap(
                city,
                MarkerStyle.NOT_VISITED,
                [],
                { addToMap: false, lazyPopup: true },
            );
            entries.push({ cityId: city.id, marker });
        } catch (error) {
            console.error(
                `Не удалось создать маркер непосещённого города #${city.id}:`,
                error,
            );
        }
    }

    this.notVisitedCityLayer.add(entries);
    this.notVisitedCityLayer.show();
    if (entries.length === 0) {
        this.finishNotVisitedLoading();
    }
}
```

Расширить `addMarkerToMap` и передать `lazyPopup` компоненту popup:

```javascript
addMarkerToMap(
    city,
    marker_style,
    users,
    { addToMap = true, lazyPopup = false } = {},
) {
    if (users === undefined) {
        const yearSelect = document.getElementById('id_year_filter');
        let selectedYear = undefined;
        if (yearSelect && yearSelect.value && yearSelect.value !== 'all') {
            selectedYear = parseInt(yearSelect.value, 10);
            if (isNaN(selectedYear)) {
                selectedYear = undefined;
            }
        }
        const usersMap = this.getUsersWhoVisitedCity(selectedYear);
        users = usersMap.get(city.id) || [];
    }

    let icon;
    let zIndexOffset;
    switch (marker_style) {
        case MarkerStyle.OWN:
            icon = icon_visited_pin;
            zIndexOffset = 40000;
            break;
        case MarkerStyle.NOT_VISITED:
            icon = icon_not_visited_pin;
            zIndexOffset = 0;
            break;
        case MarkerStyle.SUBSCRIPTION:
            icon = icon_subscription_pin;
            zIndexOffset = 20000;
            break;
        case MarkerStyle.TOGETHER:
            icon = icon_together_pin;
            zIndexOffset = 30000;
            break;
    }

    const marker = L.marker([city.lat, city.lon], { icon });
    if (addToMap) {
        marker.addTo(this.myMap);
    }
    marker.setZIndexOffset(zIndexOffset);

    const yearSelect = document.getElementById('id_year_filter');
    let selectedYear = null;
    if (yearSelect && yearSelect.value && yearSelect.value !== 'all') {
        const year = parseInt(yearSelect.value, 10);
        if (!isNaN(year)) {
            selectedYear = year;
        }
    }

    const popupCityData = {
        id: city.id,
        name: city.name,
        regionName: city.region || '',
        countryName: city.country || '',
        isVisited:
            marker_style === MarkerStyle.OWN || marker_style === MarkerStyle.TOGETHER,
        firstVisitDate: city.first_visit_date || '',
        lastVisitDate: city.last_visit_date || '',
        numberOfVisits: city.number_of_visits || 1,
        numberOfUsersWhoVisitCity: city.number_of_users_who_visit_city ?? null,
        numberOfVisitsAllUsers: city.number_of_visits_all_users ?? null,
    };

    const regionLink = city.region_id ? `/region/${city.region_id}/list` : '';
    const countryCodeFromUrl = new URLSearchParams(window.location.search).get('country');
    const countryCode = city.country_code || countryCodeFromUrl || '';
    const countryLink = countryCode
        ? `/city/all/list?country=${encodeURIComponent(countryCode)}`
        : '';
    const addButtonText =
        marker_style === MarkerStyle.SUBSCRIPTION ||
        marker_style === MarkerStyle.NOT_VISITED
            ? 'Отметить как посещённый'
            : 'Добавить ещё одно посещение';

    bindPopupToMarker(marker, popupCityData, {
        regionName: city.region || '',
        countryName: city.country || '',
        regionLink,
        countryLink,
        isAuthenticated: true,
        canMarkVisited: true,
        markerStyle: marker_style,
        subscriptionUsers: users || [],
        selectedYear,
        addButtonText,
        lazyPopup,
    });
    return marker;
}
```

- [ ] **Step 6: Разделить скрытие, полную очистку и адресное удаление**

Заменить методы управления непосещёнными маркерами:

```javascript
hideNotVisitedCities() {
    this.notVisitedCityLayer.hide();
}

removeNotVisitedMarker(cityId) {
    return this.notVisitedCityLayer.remove(cityId);
}

removeNotVisitedMarkers() {
    this.notVisitedCityLayer.clear();
}
```

В `updateMarker(city)` заменить прямое удаление красного маркера:

```javascript
if (this.stateNotVisitedCities.has(id)) {
    this.removeNotVisitedMarker(id);
    const newMarker = this.addMarkerToMap(city, MarkerStyle.OWN);
    this.stateOwnCities.set(id, newMarker);
```

Удалить лишние `this.stateNotVisitedCities.clear()` сразу после вызовов `removeNotVisitedMarkers()`: `clear()` нового слоя уже синхронно очищает индекс.

- [ ] **Step 7: Убрать прямое удаление кластерного маркера из map_city**

В callback добавления посещения в `frontend/js/entries/map_city.js` заменить блок строк 79-86:

```javascript
if (city?.id && actions) {
    actions.removeNotVisitedMarker(city.id);
}
```

- [ ] **Step 8: Запустить тесты ToolbarActions, popup и слоя**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js js/components/city_popup.test.js js/components/toolbar_actions.test.js
```

Expected: PASS, 15 tests passed.

- [ ] **Step 9: Проверить изменения задачи без коммита**

Run:

```bash
git diff --check -- frontend/js/components/toolbar_actions.js frontend/js/components/toolbar_actions.test.js frontend/js/entries/map_city.js
```

Expected: код возврата `0`, вывода нет, коммит не создан.

---

### Task 4: CSS кластера и полная верификация

**Files:**
- Modify: `frontend/js/entries/leaflet_css.js:1-2`
- Modify: `frontend/css/leaflet-controls.css`

**Interfaces:**
- Consumes: стандартные классы `leaflet.markercluster` `.marker-cluster`, `.marker-cluster-small`, `.marker-cluster-medium`, `.marker-cluster-large`.
- Produces: подключённые базовые стили плагина и красная цветовая схема кластеров непосещённых городов.

- [ ] **Step 1: Подключить стандартные стили плагина**

Добавить лицензионный блок и импорты в `frontend/js/entries/leaflet_css.js`:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import 'leaflet/dist/leaflet.css';
import 'leaflet-fullscreen/dist/leaflet.fullscreen.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
```

- [ ] **Step 2: Добавить красную цветовую схему кластеров**

В конец `frontend/css/leaflet-controls.css` добавить:

```css
/* Кластеры непосещённых городов */
#map .marker-cluster-small,
#map .marker-cluster-medium,
#map .marker-cluster-large {
    background-color: rgb(210 90 90 / 28%);
}

#map .marker-cluster-small div,
#map .marker-cluster-medium div,
#map .marker-cluster-large div {
    background-color: rgb(210 90 90 / 88%);
    color: #ffffff;
    font-weight: 600;
}

.dark #map .marker-cluster-small,
.dark #map .marker-cluster-medium,
.dark #map .marker-cluster-large {
    background-color: rgb(248 113 113 / 30%);
}

.dark #map .marker-cluster-small div,
.dark #map .marker-cluster-medium div,
.dark #map .marker-cluster-large div {
    background-color: rgb(185 28 28 / 90%);
}
```

Не добавлять тест, проверяющий CSS-токены или внешний вид; корректность подключения проверяет production-сборка, внешний вид проверяется вручную.

- [ ] **Step 3: Запустить полный набор frontend-тестов**

Run:

```bash
npm --prefix frontend test
```

Expected: PASS, все suites и tests завершены без ошибок.

- [ ] **Step 4: Собрать production-ассеты**

Run:

```bash
npm --prefix frontend run build
```

Expected: Vite завершается с кодом `0`; manifest содержит entries `map_city` и `leaflet_css`; отсутствуют unresolved imports и CSS warnings.

- [ ] **Step 5: Выполнить статические проверки изменённых файлов**

Run:

```bash
git diff --check
```

Expected: код возврата `0`, вывода нет.

Run:

```bash
poetry run pre-commit run --files frontend/package.json frontend/package-lock.json frontend/js/components/not_visited_city_layer.js frontend/js/components/not_visited_city_layer.test.js frontend/js/components/city_popup.js frontend/js/components/city_popup.test.js frontend/js/components/toolbar_actions.js frontend/js/components/toolbar_actions.test.js frontend/js/entries/map_city.js frontend/js/entries/leaflet_css.js frontend/css/leaflet-controls.css docs/superpowers/specs/2026-07-24-unvisited-city-marker-clustering-design.md docs/superpowers/plans/2026-07-24-unvisited-city-marker-clustering.md
```

Expected: все hooks завершаются `Passed` или `Skipped`, ошибок нет.

- [ ] **Step 6: Выполнить ручной performance-профиль на России**

1. Открыть основную карту с `?country=RU` и включить Chrome DevTools Performance.
2. Включить мобильную эмуляцию и CPU throttling `4x`.
3. Нажать «Показать непосещённые города» и записать загрузку, drag и несколько zoom-in/zoom-out.
4. На дальнем масштабе проверить, что DOM содержит `.marker-cluster`, а не более тысячи `.custom-icon-not_visited-pin`.
5. Убедиться, что добавление разбито на порции и не создаёт одной многосекундной long task.
6. Приблизить карту до отдельных городов, открыть popup и отметить один город посещённым.
7. Убедиться, что красный маркер исчез из кластера, зелёный маркер появился без перезагрузки.
8. Скрыть и повторно показать непосещённые города; во вкладке Network не должно быть второго API-запроса.

Expected: карта остаётся отзывчивой, кластеры раскрываются, popup и перевод города в посещённые работают, повторная загрузка и массовое повторное построение отсутствуют.

- [ ] **Step 7: Проверить итоговый рабочий набор без коммита**

Run:

```bash
git status --short
```

Expected: перечислены только намеренно изменённые файлы задачи и ранее существовавшие пользовательские изменения; коммит не создан.

---

### Task 5: Отключение полигона охвата при наведении

**Files:**
- Modify: `frontend/js/components/not_visited_city_layer.test.js:43-56`
- Modify: `frontend/js/components/not_visited_city_layer.js:17-31`

**Interfaces:**
- Consumes: параметры `L.markerClusterGroup(options)` из `leaflet.markercluster` 1.5.3.
- Produces: кластерный слой с `showCoverageOnHover: false`; zoom-to-bounds, click и spiderfy используют стандартные значения плагина.

- [ ] **Step 1: Добавить падающую проверку конфигурации**

В существующем тесте `создаёт кластер с пакетной загрузкой и передаёт прогресс наружу` расширить ожидаемый объект:

```javascript
expect(mocks.markerClusterGroup).toHaveBeenCalledWith(expect.objectContaining({
    chunkedLoading: true,
    chunkProgress: expect.any(Function),
    removeOutsideVisibleBounds: true,
    showCoverageOnHover: false,
}));
```

- [ ] **Step 2: Запустить focused-тест и подтвердить RED**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js
```

Expected: FAIL в тесте конфигурации, потому что `showCoverageOnHover` отсутствует.

- [ ] **Step 3: Отключить hover coverage штатной опцией**

В конфигурацию `L.markerClusterGroup` добавить одну опцию:

```javascript
this.clusterGroup = L.markerClusterGroup({
    chunkedLoading: true,
    chunkProgress: (processed, total, elapsed) => {
        if (processed === total && this.isBatchProcessing) {
            const pendingRemovals = [...this.pendingRemovals];
            this.pendingRemovals.clear();
            this.isBatchProcessing = false;
            pendingRemovals.forEach((marker) => {
                this.clusterGroup.removeLayer(marker);
            });
        }
        onChunkProgress?.(processed, total, elapsed);
    },
    removeOutsideVisibleBounds: true,
    showCoverageOnHover: false,
});
```

Не задавать `zoomToBoundsOnClick` и `spiderfyOnMaxZoom`: их стандартное поведение должно сохраниться.

- [ ] **Step 4: Запустить focused и полный frontend test suite**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js
```

Expected: PASS, 9 tests passed.

Run:

```bash
npm --prefix frontend test
```

Expected: PASS, 16 test files и 126 tests passed.

- [ ] **Step 5: Проверить production build и статические проверки**

Run:

```bash
npm --prefix frontend run build
```

Expected: Vite завершается с кодом `0`; unresolved imports и CSS errors отсутствуют.

Run:

```bash
poetry run pre-commit run --files frontend/js/components/not_visited_city_layer.js frontend/js/components/not_visited_city_layer.test.js docs/superpowers/specs/2026-07-24-unvisited-city-marker-clustering-design.md docs/superpowers/plans/2026-07-24-unvisited-city-marker-clustering.md
```

Expected: все применимые hooks завершаются `Passed`, остальные `Skipped`.

Run:

```bash
git diff --check
```

Expected: код возврата `0`, вывода нет, коммит не создан.
