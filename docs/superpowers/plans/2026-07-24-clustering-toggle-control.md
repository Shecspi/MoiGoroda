<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Clustering Toggle Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить на основную карту доступный Leaflet-контрол, который без повторного API-запроса переключает непосещённые города между кластерным и обычным представлением.

**Architecture:** `NotVisitedCityLayer` становится владельцем двух слоёв представления, использующих один реестр маркеров: `MarkerClusterGroup` и обычный `LayerGroup`. Отдельный UI-компонент отвечает только за Leaflet-контрол, а `ToolbarActions` сериализует переключение с текущей загрузкой и показывает существующее сообщение при ошибке.

**Tech Stack:** JavaScript, Leaflet 1.9.4, Leaflet.markercluster 1.5.3, Vitest 2.1, happy-dom 20, Vite 5.4.

## Global Constraints

- Переключатель применяется только к непосещённым городам основной карты `map_city`.
- Кластеризация включена при каждом открытии страницы.
- Выбор не сохраняется в `localStorage`, URL или на сервере.
- Оба режима используют одни и те же экземпляры маркеров и popup.
- Переключение не выполняет API-запрос и не создаёт маркеры заново.
- При выключении кластеризации все доступные непосещённые маркеры отображаются через обычный Leaflet `LayerGroup`.
- Переключение во время chunk-загрузки дожидается её завершения.
- Ошибка переключения сохраняет предыдущий режим и разрешает повторную попытку.
- Контрол находится справа сверху и поддерживает click, Enter, Space, `aria-label` и `aria-pressed`.
- Не создавать тесты, проверяющие только CSS-классы или внешний вид.
- Каждый создаваемый и изменяемый файл содержит лицензионный блок проекта.
- Не создавать коммит без новой прямой команды пользователя.

---

### Task 1: Два режима представления в NotVisitedCityLayer

**Files:**
- Modify: `frontend/js/components/not_visited_city_layer.js`
- Modify: `frontend/js/components/not_visited_city_layer.test.js`

**Interfaces:**
- Consumes: `L.markerClusterGroup`, `L.layerGroup`, карта с `addLayer`, `removeLayer`, `hasLayer`.
- Produces: `clusteringEnabled: boolean`, `visible: boolean`, `directGroup: L.LayerGroup`, `show(): Promise<void>`, `setClusteringEnabled(enabled): Promise<boolean>`, `waitForBatch(): Promise<void>`.
- Существующие `markers`, `add`, `hide`, `remove`, `clear` сохраняются.

- [ ] **Step 1: Добавить падающие lifecycle-тесты**

Расширить Leaflet mock методом `layerGroup` и объектом `directGroup` с `addLayer`, `removeLayer`, `clearLayers`. Проверить сценарии:

```javascript
it('по умолчанию показывает кластерный слой', async () => {
    const layer = new NotVisitedCityLayer(map);
    expect(layer.clusteringEnabled).toBe(true);

    const shown = layer.show();
    const {chunkProgress} = mocks.markerClusterGroup.mock.calls[0][0];
    chunkProgress(1, 1, 10);
    await shown;

    expect(map.addLayer).toHaveBeenCalledWith(clusterGroup);
    expect(map.addLayer).not.toHaveBeenCalledWith(directGroup);
});

it('добавляет одинаковые маркеры в кластерный и обычный слои', () => {
    const layer = new NotVisitedCityLayer(map);
    const marker = {id: 'city'};
    layer.add([{cityId: 1, marker}]);

    expect(clusterGroup.addLayers).toHaveBeenCalledWith([marker]);
    expect(directGroup.addLayer).toHaveBeenCalledWith(marker);
    expect(layer.markers.get(1)).toBe(marker);
});

it('переключает видимый слой без пересоздания маркеров', async () => {
    const layer = new NotVisitedCityLayer(map);
    layer.visible = true;
    map.hasLayer.mockImplementation((candidate) => candidate === clusterGroup);

    await expect(layer.setClusteringEnabled(false)).resolves.toBe(false);

    expect(map.removeLayer).toHaveBeenCalledWith(clusterGroup);
    expect(map.addLayer).toHaveBeenCalledWith(directGroup);
    expect(clusterGroup.addLayers).not.toHaveBeenCalled();
});

it('меняет будущий режим скрытого слоя без добавления на карту', async () => {
    const layer = new NotVisitedCityLayer(map);
    await layer.setClusteringEnabled(false);

    expect(layer.clusteringEnabled).toBe(false);
    expect(map.addLayer).not.toHaveBeenCalled();
    expect(map.removeLayer).not.toHaveBeenCalled();
});

it('удаляет и очищает маркеры в обоих слоях', () => {
    const layer = new NotVisitedCityLayer(map);
    const marker = {id: 'city'};
    layer.add([{cityId: 1, marker}]);
    layer.remove(1);
    layer.clear();

    expect(clusterGroup.removeLayer).toHaveBeenCalledWith(marker);
    expect(directGroup.removeLayer).toHaveBeenCalledWith(marker);
    expect(clusterGroup.clearLayers).toHaveBeenCalled();
    expect(directGroup.clearLayers).toHaveBeenCalled();
});
```

Тестовый набор также фиксирует два сценария: Promise выключения остаётся pending до финального `chunkProgress`, а ошибка `map.addLayer(nextGroup)` возвращает на карту `previousGroup`, сохраняет прежний `clusteringEnabled` и повторно выбрасывает исходную ошибку.

- [ ] **Step 2: Подтвердить RED**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js
```

Expected: FAIL из-за отсутствующих `directGroup`, `clusteringEnabled` и `setClusteringEnabled`.

- [ ] **Step 3: Реализовать общий реестр и два слоя**

В конструкторе создать состояние:

```javascript
this.directGroup = L.layerGroup();
this.clusteringEnabled = true;
this.visible = false;
this.batchWaiters = [];
```

В финальном `chunkProgress` после обработки pending removals разрешать ожидающих:

```javascript
const waiters = this.batchWaiters.splice(0);
waiters.forEach((resolve) => resolve());
```

Добавить методы:

```javascript
waitForBatch() {
    if (!this.isBatchProcessing) {
        return Promise.resolve();
    }
    return new Promise((resolve) => this.batchWaiters.push(resolve));
}

getActiveGroup() {
    return this.clusteringEnabled ? this.clusterGroup : this.directGroup;
}

async show() {
    this.visible = true;
    const activeGroup = this.getActiveGroup();
    if (!this.map.hasLayer(activeGroup)) {
        this.map.addLayer(activeGroup);
    }
    if (this.clusteringEnabled) {
        await this.waitForBatch();
    }
}

hide() {
    const activeGroup = this.getActiveGroup();
    if (this.map.hasLayer(activeGroup)) {
        this.map.removeLayer(activeGroup);
    }
    this.visible = false;
}

async setClusteringEnabled(enabled) {
    if (enabled === this.clusteringEnabled) {
        return this.clusteringEnabled;
    }
    const previousEnabled = this.clusteringEnabled;
    const previousGroup = this.getActiveGroup();
    if (!this.visible) {
        this.clusteringEnabled = enabled;
        return this.clusteringEnabled;
    }
    if (previousEnabled) {
        await this.waitForBatch();
    }
    const nextGroup = enabled ? this.clusterGroup : this.directGroup;
    try {
        if (this.map.hasLayer(previousGroup)) {
            this.map.removeLayer(previousGroup);
        }
        this.clusteringEnabled = enabled;
        this.map.addLayer(nextGroup);
        if (enabled) {
            await this.waitForBatch();
        }
        return this.clusteringEnabled;
    } catch (error) {
        try {
            if (this.map.hasLayer(nextGroup)) {
                this.map.removeLayer(nextGroup);
            }
        } catch (cleanupError) {
            console.error('Ошибка при откате слоя кластеризации:', cleanupError);
        }
        this.clusteringEnabled = previousEnabled;
        try {
            if (!this.map.hasLayer(previousGroup)) {
                this.map.addLayer(previousGroup);
            }
        } catch (cleanupError) {
            console.error('Ошибка при восстановлении слоя кластеризации:', cleanupError);
        }
        throw error;
    }
}
```

В `add` передавать каждый новый marker в `directGroup.addLayer(marker)`; при rollback очищать оба слоя. В `remove` вызывать `directGroup.removeLayer(marker)`. В `clear` вызывать `clearLayers()` обоих слоёв, обнулять `visible`, batch-state, pending removals и разрешать `batchWaiters`, чтобы ожидающие операции не зависали.

Pending removal добавлять только когда кластерный слой находится на карте и batch активен:

```javascript
if (this.isBatchProcessing && this.map.hasLayer(this.clusterGroup)) {
    this.pendingRemovals.add(marker);
}
```

- [ ] **Step 4: Запустить тесты слоя**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js
```

Expected: PASS, все тесты слоя проходят без зависших Promise.

---

### Task 2: Доступный Leaflet-контрол кластеризации

**Files:**
- Create: `frontend/js/components/not_visited_clustering_control.js`
- Create: `frontend/js/components/not_visited_clustering_control.test.js`

**Interfaces:**
- Consumes: `getEnabled(): boolean`, `onToggle(): Promise<boolean> | boolean`.
- Produces: `addNotVisitedClusteringControl(map, handlers): L.Control`.

- [ ] **Step 1: Написать падающие тесты контрола**

Тестовый Leaflet mock должен реализовать `Control.extend`, `DomUtil.create`, `DomEvent.on`, `preventDefault`, `stopPropagation`, `disableClickPropagation`, `disableScrollPropagation`. Проверить:

```javascript
it('по умолчанию отражает включённую кластеризацию', () => {
    const control = addNotVisitedClusteringControl(map, {
        getEnabled: () => true,
        onToggle: vi.fn(),
    });
    const button = control.getContainer().querySelector('[role="button"]');

    expect(button.getAttribute('aria-pressed')).toBe('true');
    expect(button.getAttribute('aria-label')).toBe('Отключить кластеризацию');
    expect(button.classList.contains('custom-control-for-map--active')).toBe(true);
});

it('переключает режим мышью и синхронизирует aria', async () => {
    let enabled = true;
    const onToggle = vi.fn(async () => (enabled = !enabled));
    const control = addNotVisitedClusteringControl(map, {
        getEnabled: () => enabled,
        onToggle,
    });
    const button = control.getContainer().querySelector('[role="button"]');

    button.click();
    await vi.waitFor(() => expect(onToggle).toHaveBeenCalledOnce());
    expect(button.getAttribute('aria-pressed')).toBe('false');
    expect(button.getAttribute('aria-label')).toBe('Включить кластеризацию');
});
```

Тестовый набор также вызывает зарегистрированный `keydown` с `Enter` и Space, проверяет один вызов `onToggle` при повторной активации до завершения Promise и после rejected Promise ожидает `aria-disabled="false"` с состоянием из `getEnabled()`.

- [ ] **Step 2: Подтвердить RED**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js
```

Expected: FAIL с ошибкой отсутствующего модуля.

- [ ] **Step 3: Реализовать контрол**

Создать компонент по паттерну `region_city_display_control.js`:

```javascript
// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import L from 'leaflet';

const ICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="control-icon" fill="none" stroke="currentColor" aria-hidden="true"><circle cx="8" cy="8" r="3"/><circle cx="16" cy="9" r="3"/><circle cx="12" cy="16" r="3"/><path d="M10.5 9.5l1 4M13.5 11l-1 2.5"/></svg>';

export function addNotVisitedClusteringControl(map, {getEnabled, onToggle}) {
    const Control = L.Control.extend({
        onAdd() {
            const wrap = L.DomUtil.create('div', 'leaflet-bar');
            const button = L.DomUtil.create('a', 'custom-control-for-map', wrap);
            button.href = '#';
            button.innerHTML = ICON;
            button.setAttribute('role', 'button');
            button.setAttribute('tabindex', '0');
            let pending = false;

            const syncUi = () => {
                const enabled = getEnabled();
                button.classList.toggle('custom-control-for-map--active', enabled);
                button.classList.toggle('custom-control-for-map--disabled', pending);
                button.setAttribute('aria-disabled', String(pending));
                button.setAttribute('aria-pressed', String(enabled));
                button.title = enabled ? 'Отключить кластеризацию' : 'Включить кластеризацию';
                button.setAttribute('aria-label', button.title);
            };

            const activate = async (event) => {
                L.DomEvent.preventDefault(event);
                L.DomEvent.stopPropagation(event);
                if (pending) return;
                pending = true;
                syncUi();
                try {
                    await onToggle();
                } catch (error) {
                    console.error('Ошибка при переключении кластеризации:', error);
                } finally {
                    pending = false;
                    syncUi();
                }
            };

            L.DomEvent.disableClickPropagation(wrap);
            L.DomEvent.disableScrollPropagation(wrap);
            L.DomEvent.on(button, 'click', activate);
            L.DomEvent.on(button, 'keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    void activate(event);
                }
            });
            syncUi();
            return wrap;
        },
    });
    const control = new Control({position: 'topright'});
    control.addTo(map);
    return control;
}
```

- [ ] **Step 4: Запустить тесты контрола**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js
```

Expected: PASS, click и keyboard сценарии проходят, rejected Promise не оставляет disabled UI.

---

### Task 3: Интеграция с ToolbarActions и основной картой

**Files:**
- Modify: `frontend/js/components/toolbar_actions.js`
- Modify: `frontend/js/components/toolbar_actions.test.js`
- Modify: `frontend/js/entries/map_city.js`

**Interfaces:**
- Consumes: `NotVisitedCityLayer.setClusteringEnabled`, `waitForBatch`, `addNotVisitedClusteringControl`.
- Produces: `ToolbarActions.isNotVisitedClusteringEnabled(): boolean`, `ToolbarActions.toggleNotVisitedClustering(): Promise<boolean>`.

- [ ] **Step 1: Добавить падающие integration-тесты**

В тестах ToolbarActions проверить deduplication и ожидание активного show:

```javascript
it('переключает кластеризацию только после активной загрузки', async () => {
    const actions = createActions();
    let finishShow;
    actions.notVisitedShowPromise = new Promise((resolve) => (finishShow = resolve));
    actions.notVisitedCityLayer.clusteringEnabled = true;
    actions.notVisitedCityLayer.setClusteringEnabled = vi.fn().mockResolvedValue(false);

    const toggle = actions.toggleNotVisitedClustering();
    expect(actions.notVisitedCityLayer.setClusteringEnabled).not.toHaveBeenCalled();
    finishShow(true);
    await expect(toggle).resolves.toBe(false);
    expect(actions.notVisitedCityLayer.setClusteringEnabled).toHaveBeenCalledWith(false);
});

it('дедуплицирует параллельные переключения', () => {
    const actions = createActions();
    actions.notVisitedCityLayer.setClusteringEnabled = vi.fn(() => new Promise(() => {}));
    expect(actions.toggleNotVisitedClustering()).toBe(actions.toggleNotVisitedClustering());
});
```

Error-path тест настраивает первый `setClusteringEnabled` как rejected Promise, ожидает текущий режим и вызов `addErrorControl`, затем настраивает второй вызов как успешный и подтверждает повторную попытку. Существующие tests `show`, `hide`, `removeNotVisitedMarkers` ожидают Promise из `NotVisitedCityLayer.show()` и активный clustering toggle перед полной очисткой.

В static contract-тесте `map_city.js` проверить импорт и вызов `addNotVisitedClusteringControl` после создания `ToolbarActions`.

- [ ] **Step 2: Подтвердить RED**

Run:

```bash
npm --prefix frontend test -- js/components/toolbar_actions.test.js
```

Expected: FAIL из-за отсутствующих методов toggle и интеграции контрола.

- [ ] **Step 3: Упростить ожидание chunk через Promise слоя**

Удалить `notVisitedChunkResolve` и callback, который вручную завершает chunk Promise. Создавать слой без callback:

```javascript
this.notVisitedClusteringTogglePromise = null;
this.notVisitedCityLayer = new NotVisitedCityLayer(this.myMap);
this.stateNotVisitedCities = this.notVisitedCityLayer.markers;
```

Сделать `addNotVisitedCitiesOnMap` async. После `add(entries)` ожидать `show()` и только затем фиксировать built-state:

```javascript
this.notVisitedCityLayer.add(entries);
await this.notVisitedCityLayer.show();
this.notVisitedCitiesBuilt = true;
this.finishNotVisitedLoading();
```

В ветке готового слоя также использовать `await this.notVisitedCityLayer.show()`.

- [ ] **Step 4: Добавить сериализованный toggle в ToolbarActions**

```javascript
isNotVisitedClusteringEnabled() {
    return this.notVisitedCityLayer.clusteringEnabled;
}

toggleNotVisitedClustering() {
    if (this.notVisitedClusteringTogglePromise) {
        return this.notVisitedClusteringTogglePromise;
    }
    const operation = this.performToggleNotVisitedClustering();
    const tracked = operation.finally(() => {
        if (this.notVisitedClusteringTogglePromise === tracked) {
            this.notVisitedClusteringTogglePromise = null;
        }
    });
    this.notVisitedClusteringTogglePromise = tracked;
    return tracked;
}

async performToggleNotVisitedClustering() {
    if (this.notVisitedShowPromise) {
        await this.notVisitedShowPromise;
    }
    const nextEnabled = !this.notVisitedCityLayer.clusteringEnabled;
    try {
        return await this.notVisitedCityLayer.setClusteringEnabled(nextEnabled);
    } catch (error) {
        console.error('Ошибка при переключении кластеризации:', error);
        addErrorControl(this.myMap, 'Произошла ошибка при переключении кластеризации');
        return this.notVisitedCityLayer.clusteringEnabled;
    }
}
```

`removeNotVisitedMarkers()` должен ожидать snapshot обоих Promise перед `clear()`:

```javascript
const activeShow = this.notVisitedShowPromise;
const activeToggle = this.notVisitedClusteringTogglePromise;
await Promise.all([activeShow, activeToggle].filter(Boolean));
this.notVisitedCityLayer.clear();
this.notVisitedCitiesBuilt = false;
```

- [ ] **Step 5: Добавить контрол в map_city**

Импортировать компонент:

```javascript
import {addNotVisitedClusteringControl} from '../components/not_visited_clustering_control.js';
```

Сразу после `actions = new ToolbarActions(map, own_cities);` добавить:

```javascript
addNotVisitedClusteringControl(map, {
    getEnabled: () => actions.isNotVisitedClusteringEnabled(),
    onToggle: () => actions.toggleNotVisitedClustering(),
});
```

- [ ] **Step 6: Запустить focused suites**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_city_layer.test.js js/components/not_visited_clustering_control.test.js js/components/toolbar_actions.test.js
```

Expected: PASS, все lifecycle, control и integration tests проходят.

---

### Task 4: Полная верификация

**Files:**
- Verify only: все файлы Tasks 1–3 и обновлённая спецификация.

- [ ] **Step 1: Запустить полный frontend suite**

Run:

```bash
npm --prefix frontend test
```

Expected: PASS, все test files проходят без зависших Promise и console errors.

- [ ] **Step 2: Собрать production assets**

Run:

```bash
npm --prefix frontend run build
```

Expected: Vite завершается с кодом `0`; `map_city` и Leaflet assets собираются без unresolved imports и CSS errors.

- [ ] **Step 3: Запустить pre-commit и diff check**

Run:

```bash
poetry run pre-commit run --files frontend/js/components/not_visited_city_layer.js frontend/js/components/not_visited_city_layer.test.js frontend/js/components/not_visited_clustering_control.js frontend/js/components/not_visited_clustering_control.test.js frontend/js/components/toolbar_actions.js frontend/js/components/toolbar_actions.test.js frontend/js/entries/map_city.js docs/superpowers/specs/2026-07-24-unvisited-city-marker-clustering-design.md docs/superpowers/plans/2026-07-24-clustering-toggle-control.md
```

Expected: применимые hooks завершаются `Passed`, остальные `Skipped`.

Run:

```bash
git diff --check
```

Expected: код возврата `0`, вывода нет, коммит не создан.

- [ ] **Step 4: Ручная проверка**

На основной карте с `?country=RU` проверить:

1. Контрол находится справа сверху и при загрузке активен.
2. Click, Enter и Space выключают и включают кластеризацию.
3. При выключении видны отдельные красные маркеры; при включении возвращаются кластеры.
4. Переключение не создаёт запрос к API непосещённых городов.
5. Popup и отметка города посещённым работают в обоих режимах.
6. Переключение до первого показа городов задаёт будущий режим.
7. После перезагрузки кластеризация снова включена.
8. Быстрые повторные клики не запускают параллельные переключения.

Expected: состояние контрола, слой карты и ARIA синхронизированы; ошибок в console нет.

---

### Task 8: SVG, нейтральное active-состояние и видимость контрола

**Files:**
- Modify: `frontend/js/components/not_visited_clustering_control.js`
- Modify: `frontend/js/components/not_visited_clustering_control.test.js`
- Modify: `frontend/css/leaflet-controls.css`

**Interfaces:**
- Consumes: `getEnabled(): boolean`, `getVisible(): boolean`, `onToggle(): Promise<boolean> | boolean`.
- Produces: `addNotVisitedClusteringControl(map, handlers): L.Control`, `syncNotVisitedClusteringControl(control): void`.

- [ ] **Step 1: Добавить падающие тесты SVG и фактической видимости**

В `not_visited_clustering_control.test.js` передавать изменяемый `visible` через `getVisible`. Проверить, что контейнер первоначально имеет `hidden=true`, использует предоставленный solid SVG, после внешнего изменения и вызова sync становится видимым, а после обратного изменения снова скрывается:

Во всех существующих тестах контрола также передать `getVisible: () => true`, чтобы их областью проверки оставались toggle, keyboard и error-сценарии, а не начальная скрытость.

```javascript
let visible = false;
const control = addNotVisitedClusteringControl(map, {
    getEnabled: () => true,
    getVisible: () => visible,
    onToggle: vi.fn(),
});
const container = control.getContainer();
const button = getButton(control);

expect(container.hidden).toBe(true);
expect(button.querySelector('svg')?.getAttribute('viewBox')).toBe('0 0 640 640');
expect(button.querySelector('path')?.getAttribute('d')).toBe(
    'M482.4 221.9C517.7 213.6 544 181.9 544 144C544 99.8 508.2 64 464 64C420.6 64 385.3 98.5 384 141.5L200.2 215.1C185.7 200.8 165.9 192 144 192C99.8 192 64 227.8 64 272C64 316.2 99.8 352 144 352C156.2 352 167.8 349.3 178.1 344.4L323.7 471.8C321.3 479.4 320 487.6 320 496C320 540.2 355.8 576 400 576C444.2 576 480 540.2 480 496C480 468.3 466 443.9 444.6 429.6L482.4 221.9zM220.3 296.2C222.5 289.3 223.8 282 224 274.5L407.8 201C411.4 204.5 415.2 207.7 419.4 210.5L381.6 418.1C376.1 419.4 370.8 421.2 365.8 423.6L220.3 296.2z',
);

visible = true;
syncNotVisitedClusteringControl(control);
expect(container.hidden).toBe(false);

visible = false;
syncNotVisitedClusteringControl(control);
expect(container.hidden).toBe(true);
```

- [ ] **Step 2: Подтвердить RED**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js
```

Expected: FAIL из-за отсутствующих `getVisible`, `syncNotVisitedClusteringControl` и нового SVG.

- [ ] **Step 3: Реализовать SVG и синхронизацию контрола**

Заменить `ICON` на предоставленный SVG с классом `control-icon control-icon--solid`. Расширить handlers параметром `getVisible`. В `syncUi()` устанавливать `bar.hidden = !getVisible()`. Сохранить функцию синхронизации на контейнере и экспортировать безопасный внешний вызов:

```javascript
bar._mgSyncNotVisitedClustering = syncUi;

export function syncNotVisitedClusteringControl(control) {
    const container = control.getContainer();
    if (typeof container?._mgSyncNotVisitedClustering === 'function') {
        container._mgSyncNotVisitedClustering();
    }
}
```

Скрытый `bar` автоматически исключает кнопку из отображения и keyboard navigation через стандартный HTML `hidden`.

- [ ] **Step 4: Добавить специфичный серый active-стиль**

В `leaflet-controls.css` добавить после общих `custom-control-for-map--active` правил специфичные селекторы:

```css
#map .leaflet-control-not-visited-clustering .custom-control-for-map--active {
    background-color: #e5e7eb;
    border-color: #9ca3af;
    color: #4b5563;
}

#map .leaflet-control-not-visited-clustering .custom-control-for-map--active:hover {
    background-color: #d1d5db;
}

.dark #map .leaflet-control-not-visited-clustering .custom-control-for-map--active {
    background-color: #404040;
    border-color: #737373;
    color: #d4d4d4;
}

.dark #map .leaflet-control-not-visited-clustering .custom-control-for-map--active:hover {
    background-color: #525252;
}
```

- [ ] **Step 5: Запустить тесты контрола**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js
```

Expected: PASS; SVG, click, Enter, Space, pending/error и внешняя видимость синхронизированы.

---

### Task 9: Подписка ToolbarActions на видимость слоя

**Files:**
- Modify: `frontend/js/components/toolbar_actions.js`
- Modify: `frontend/js/components/toolbar_actions.test.js`
- Modify: `frontend/js/entries/map_city.js`

**Interfaces:**
- Produces: `ToolbarActions.isNotVisitedCitiesVisible(): boolean`, `ToolbarActions.subscribeNotVisitedVisibility(listener): () => void`.
- Consumes: `syncNotVisitedClusteringControl(control)` из Task 8.

- [ ] **Step 1: Добавить падающие тесты подписки**

В `toolbar_actions.test.js` проверить начальный вызов подписчика, уведомление после успешного show/hide/clear, уведомление после ошибочного show и удаление подписки:

```javascript
const listener = vi.fn();
const unsubscribe = actions.subscribeNotVisitedVisibility(listener);
expect(listener).toHaveBeenLastCalledWith(false);

actions.notVisitedCityLayer.visible = true;
await actions.addNotVisitedCitiesOnMap();
expect(listener).toHaveBeenLastCalledWith(true);

unsubscribe();
actions.notVisitedCityLayer.visible = false;
await actions.hideNotVisitedCities();
expect(listener).toHaveBeenCalledTimes(2);
```

Mock слоя должен обновлять `visible` в `show`, `hide` и `clear`, чтобы тест проверял фактическое состояние, а не аргумент уведомления.

- [ ] **Step 2: Подтвердить RED**

Run:

```bash
npm --prefix frontend test -- js/components/toolbar_actions.test.js
```

Expected: FAIL из-за отсутствующих subscription API и уведомлений lifecycle.

- [ ] **Step 3: Реализовать подписку и единый wrapper показа**

В конструкторе создать `this.notVisitedVisibilityListeners = new Set()`. Добавить:

```javascript
isNotVisitedCitiesVisible() {
    return this.notVisitedCityLayer.visible;
}

subscribeNotVisitedVisibility(listener) {
    this.notVisitedVisibilityListeners.add(listener);
    listener(this.isNotVisitedCitiesVisible());
    return () => this.notVisitedVisibilityListeners.delete(listener);
}

notifyNotVisitedVisibility() {
    const visible = this.isNotVisitedCitiesVisible();
    this.notVisitedVisibilityListeners.forEach((listener) => listener(visible));
}
```

Существующее содержимое `addNotVisitedCitiesOnMap()` перенести в `performAddNotVisitedCitiesOnMap()`, а публичный метод сделать wrapper с `finally`:

```javascript
async addNotVisitedCitiesOnMap() {
    try {
        return await this.performAddNotVisitedCitiesOnMap();
    } finally {
        this.notifyNotVisitedVisibility();
    }
}
```

Аналогично вызывать `notifyNotVisitedVisibility()` в `finally` методов `hideNotVisitedCities()` и `removeNotVisitedMarkers()`. Уведомление всегда читает `notVisitedCityLayer.visible`, поэтому ошибки не создают ложного UI-состояния.

- [ ] **Step 4: Подключить подписку в map_city**

Импортировать обе функции контрола и передать фактическую видимость:

```javascript
import {
    addNotVisitedClusteringControl,
    syncNotVisitedClusteringControl,
} from '../components/not_visited_clustering_control.js';

const clusteringControl = addNotVisitedClusteringControl(map, {
    getEnabled: () => actions.isNotVisitedClusteringEnabled(),
    getVisible: () => actions.isNotVisitedCitiesVisible(),
    onToggle: () => actions.toggleNotVisitedClustering(),
});
actions.subscribeNotVisitedVisibility(() => {
    syncNotVisitedClusteringControl(clusteringControl);
});
```

Обновить static contract-тест `map_city` на импорт, `getVisible` и подписку.

- [ ] **Step 5: Запустить focused suites**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js js/components/toolbar_actions.test.js
```

Expected: PASS; контрол скрыт до show, виден после show и скрыт после hide/clear/error.

---

### Task 10: Финальная верификация уточнённого контрола

**Files:**
- Verify only: файлы Tasks 8–9, спецификация и этот план.

- [ ] **Step 1: Запустить полный frontend suite**

Run: `npm --prefix frontend test`

Expected: PASS без зависших Promise и неперехваченных console errors.

- [ ] **Step 2: Собрать production assets**

Run: `npm --prefix frontend run build`

Expected: Vite завершается с кодом `0`; новый SVG и CSS включены в `map_city` assets.

- [ ] **Step 3: Запустить project hooks и diff check**

Run:

```bash
poetry run pre-commit run --files frontend/js/components/not_visited_clustering_control.js frontend/js/components/not_visited_clustering_control.test.js frontend/css/leaflet-controls.css frontend/js/components/toolbar_actions.js frontend/js/components/toolbar_actions.test.js frontend/js/entries/map_city.js docs/superpowers/specs/2026-07-24-unvisited-city-marker-clustering-design.md docs/superpowers/plans/2026-07-24-clustering-toggle-control.md
git diff --check
```

Expected: все применимые hooks проходят; `git diff --check` не выводит ошибок; коммит не создаётся.

---

### Task 11: Иконка следующего действия без серого active-состояния

**Files:**
- Modify: `frontend/js/components/not_visited_clustering_control.js`
- Modify: `frontend/js/components/not_visited_clustering_control.test.js`
- Modify: `frontend/css/leaflet-controls.css`

**Interfaces:**
- Consumes: `getEnabled(): boolean`, текущее состояние `pending`, существующую функцию `syncUi()`.
- Produces: action-oriented SVG и подпись кнопки; `aria-pressed` по-прежнему отражает текущий режим кластеризации.

- [ ] **Step 1: Обновить тесты и подтвердить RED**

В тесте начального включённого состояния ожидать действие перехода к отдельным маркерам:

```javascript
expect(button.getAttribute('aria-pressed')).toBe('true');
expect(button.getAttribute('aria-label')).toBe('Показать города отдельно');
expect(button.querySelector('svg')?.getAttribute('viewBox')).toBe('0 0 384 512');
expect(button.querySelector('path')?.getAttribute('d')).toBe(
    'M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z',
);
```

После выключения кластеризации ожидать действие обратного перехода с текущей иконкой кластера:

```javascript
await vi.waitFor(() => expect(button.getAttribute('aria-pressed')).toBe('false'));
expect(button.getAttribute('aria-label')).toBe('Собрать города в кластеры');
expect(button.querySelector('svg')?.getAttribute('viewBox')).toBe('0 0 640 640');
expect(button.querySelector('path')?.getAttribute('d')).toBe(
    'M482.4 221.9C517.7 213.6 544 181.9 544 144C544 99.8 508.2 64 464 64C420.6 64 385.3 98.5 384 141.5L200.2 215.1C185.7 200.8 165.9 192 144 192C99.8 192 64 227.8 64 272C64 316.2 99.8 352 144 352C156.2 352 167.8 349.3 178.1 344.4L323.7 471.8C321.3 479.4 320 487.6 320 496C320 540.2 355.8 576 400 576C444.2 576 480 540.2 480 496C480 468.3 466 443.9 444.6 429.6L482.4 221.9zM220.3 296.2C222.5 289.3 223.8 282 224 274.5L407.8 201C411.4 204.5 415.2 207.7 419.4 210.5L381.6 418.1C376.1 419.4 370.8 421.2 365.8 423.6L220.3 296.2z',
);
```

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js
```

Expected: FAIL, потому что включённое состояние пока показывает кластерный SVG и старую подпись.

- [ ] **Step 2: Реализовать смену иконки действия**

В `not_visited_clustering_control.js` переименовать текущую константу в `CLUSTER_ACTION_ICON` без изменения SVG и добавить маркерный SVG на основе используемого проектом глифа `locationPinSvg`:

```javascript
const MARKER_ACTION_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" class="control-icon control-icon--solid" aria-hidden="true">' +
    '<path d="M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/>' +
    '</svg>';
```

В `syncUi()` убрать переключение `custom-control-for-map--active` и синхронизировать SVG и подпись с действием следующего нажатия:

```javascript
button.innerHTML = enabled ? MARKER_ACTION_ICON : CLUSTER_ACTION_ICON;
button.title = enabled
    ? 'Показать города отдельно'
    : 'Собрать города в кластеры';
button.setAttribute('aria-label', button.title);
```

Сохранить `aria-pressed=enabled`, чтобы assistive technologies получали фактическое состояние, и `custom-control-for-map--disabled=pending`, чтобы блокировка отображалась только во время переключения.

- [ ] **Step 3: Удалить специфичные серые стили контрола**

Удалить из `frontend/css/leaflet-controls.css` четыре правила для:

```css
#map .leaflet-control-not-visited-clustering .custom-control-for-map--active
#map .leaflet-control-not-visited-clustering .custom-control-for-map--active:hover
.dark #map .leaflet-control-not-visited-clustering .custom-control-for-map--active
.dark #map .leaflet-control-not-visited-clustering .custom-control-for-map--active:hover
```

Общие стили `.custom-control-for-map`, hover, focus и временный disabled не менять.

- [ ] **Step 4: Запустить focused-тест и подтвердить GREEN**

Run:

```bash
npm --prefix frontend test -- js/components/not_visited_clustering_control.test.js
```

Expected: PASS; начальное состояние показывает marker action, выключенное состояние показывает текущий cluster action, ARIA и pending/error-сценарии остаются синхронизированы.

- [ ] **Step 5: Выполнить полную верификацию frontend**

Run:

```bash
npm --prefix frontend test
npm --prefix frontend run build
poetry run pre-commit run --files frontend/js/components/not_visited_clustering_control.js frontend/js/components/not_visited_clustering_control.test.js frontend/css/leaflet-controls.css docs/superpowers/specs/2026-07-24-unvisited-city-marker-clustering-design.md docs/superpowers/plans/2026-07-24-clustering-toggle-control.md
git diff --check
```

Expected: все тесты и hooks проходят; Vite build завершается с кодом `0`; `git diff --check` не выводит ошибок; коммит не создаётся.
