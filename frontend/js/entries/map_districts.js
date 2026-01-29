/**
 * Реализует отображение карты районов города с полигонами из GeoJSON.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */
import L from 'leaflet';
import {create_map, addLoadControl, addErrorControl} from '../components/map.js';
import {showDangerToast, showSuccessToast} from '../components/toast.js';
import {getCookie} from '../components/get_cookie.js';
import {pluralize} from '../components/search_services.js';

let map;
let districtsData = new Map(); // district_name -> {id, is_visited, area, population}
let geoJsonLayers = [];
let currentCityId = null;
let cachedGeoJson = null;

// Цвета и ширина по умолчанию для сброса настроек
const DEFAULT_COLOR_VISITED = '#4fbf4f';
const DEFAULT_COLOR_NOT_VISITED = '#bbbbbb';
const DEFAULT_COLOR_BORDER = '#444444';
const DEFAULT_BORDER_WEIGHT = 1;
const BORDER_WEIGHT_MIN = 1;
const BORDER_WEIGHT_MAX = 10;
const DEFAULT_FILL_OPACITY_VISITED = 60;
const DEFAULT_FILL_OPACITY_NOT_VISITED = 60;
const DEFAULT_BORDER_OPACITY = 40;
const OPACITY_MIN = 0;
const OPACITY_MAX = 100;
const OPACITY_STEP = 10;

// Стили для полигонов (используются те же параметры, что и на карте регионов)
const visitedStyle = {
    fillColor: DEFAULT_COLOR_VISITED, // зелёный для 41-60% посещённости - более светлый оттенок
    fillOpacity: DEFAULT_FILL_OPACITY_VISITED / 100,
    color: DEFAULT_COLOR_BORDER,
    weight: DEFAULT_BORDER_WEIGHT,
    opacity: DEFAULT_BORDER_OPACITY / 100,
};

const notVisitedStyle = {
    fillColor: DEFAULT_COLOR_NOT_VISITED, // серый - цвет для непосещённого региона
    fillOpacity: DEFAULT_FILL_OPACITY_NOT_VISITED / 100,
    color: DEFAULT_COLOR_BORDER,
    weight: DEFAULT_BORDER_WEIGHT,
    opacity: DEFAULT_BORDER_OPACITY / 100,
};

const defaultStyle = {
    fillColor: 'red',
    fillOpacity: DEFAULT_FILL_OPACITY_NOT_VISITED / 100,
    color: DEFAULT_COLOR_BORDER,
    weight: DEFAULT_BORDER_WEIGHT,
    opacity: DEFAULT_BORDER_OPACITY / 100,
};

/** Проверяет, что строка — цвет в формате #rrggbb (7 символов). */
function isValidHexColor(value) {
    if (typeof value !== 'string' || value.length !== 7 || value[0] !== '#') return false;
    return /^#[0-9a-fA-F]{6}$/.test(value);
}

/**
 * Применяет выбранные пользователем цвета к полигонам (перерисовывает карту).
 * defaultStyle не меняется.
 */
function applyPolygonColors() {
    if (!cachedGeoJson || !districtsData.size) return;
    displayDistrictsOnMap(cachedGeoJson, districtsData);
}

/**
 * Возвращает функцию, вызывающую callback не чаще чем раз в intervalMs.
 * Последний вызов после остановки серии выполняется через requestAnimationFrame
 * или по таймеру, чтобы финальное состояние не терялось.
 */
function throttle(intervalMs, callback) {
    let lastRun = 0;
    let scheduled = null;
    return function throttled(...args) {
        const now = Date.now();
        const elapsed = now - lastRun;
        if (elapsed >= intervalMs || lastRun === 0) {
            if (scheduled) {
                cancelAnimationFrame(scheduled);
                scheduled = null;
            }
            lastRun = now;
            callback.apply(this, args);
        } else if (!scheduled) {
            scheduled = requestAnimationFrame(() => {
                scheduled = null;
                lastRun = Date.now();
                callback.apply(this, args);
            });
        }
    };
}

/** Перерисовка полигонов по цвету, не чаще чем раз в 120 ms при движении ползунка. */
const applyPolygonColorsThrottled = throttle(120, applyPolygonColors);

/** Селекторы панели и кнопки настроек цветов (для переключения видимости). */
const DISTRICT_COLORS_PANEL_SELECTOR = '#map .district-colors-panel';
const DISTRICT_COLORS_TOGGLE_BTN_SELECTOR = '#map .district-colors-toggle-btn';

/**
 * Добавляет на карту раскрывающийся контрол с выбором цветов заливки полигонов.
 * По умолчанию видна кнопка с шестерёнкой (настройки); по клику раскрывается блок с цветами.
 * По аналогии с легендой в map_region.js.
 */
function addColorPickersControl(map) {
    // Панель с выбором цветов (скрыта по умолчанию)
    const panelControl = L.control({position: 'topright'});
    panelControl.onAdd = function () {
        const div = L.DomUtil.create('div', 'leaflet-control district-colors-panel');
        div.style.display = 'none';
        div.innerHTML = `
            <div class="district-colors-panel-title">
                <span>Цвета полигонов</span>
                <button type="button" id="toggle-district-colors-btn" class="district-colors-close-btn" title="Скрыть">×</button>
            </div>
            <div class="leaflet-control-district-colors-inner">
                <div class="district-colors-section">
                    <div class="district-colors-section-title">Посещённые</div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="color-visited" class="leaflet-control-district-colors-label">Цвет</label>
                        <input type="color" id="color-visited" value="#4fbf4f" class="leaflet-control-district-colors-input" title="Цвет заливки посещённых районов">
                    </div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="fill-opacity-visited-input" class="leaflet-control-district-colors-label">Непрозрачность</label>
                        <div class="py-1 px-1.5 inline-block bg-layer border border-layer-line rounded-lg" data-district-input-number>
                            <div class="flex items-center gap-x-1.5">
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Уменьшить" data-district-input-number-decrement>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>
                                </button>
                                <input id="fill-opacity-visited-input" class="p-0 w-6 bg-transparent border-0 text-foreground placeholder:text-muted-foreground-1 text-center focus:ring-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none" style="-moz-appearance: textfield;" type="number" min="0" max="100" value="60" step="10" aria-roledescription="Число" title="Непрозрачность 0–100%, шаг 10" data-district-input-number-input>
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Увеличить" data-district-input-number-increment>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="district-colors-section">
                    <div class="district-colors-section-title">Не посещённые</div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="color-not-visited" class="leaflet-control-district-colors-label">Цвет</label>
                        <input type="color" id="color-not-visited" value="#bbbbbb" class="leaflet-control-district-colors-input" title="Цвет заливки непосещённых районов">
                    </div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="fill-opacity-not-visited-input" class="leaflet-control-district-colors-label">Непрозрачность</label>
                        <div class="py-1 px-1.5 inline-block bg-layer border border-layer-line rounded-lg" data-district-input-number>
                            <div class="flex items-center gap-x-1.5">
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Уменьшить" data-district-input-number-decrement>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>
                                </button>
                                <input id="fill-opacity-not-visited-input" class="p-0 w-6 bg-transparent border-0 text-foreground placeholder:text-muted-foreground-1 text-center focus:ring-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none" style="-moz-appearance: textfield;" type="number" min="0" max="100" value="60" step="10" aria-roledescription="Число" title="Непрозрачность 0–100%, шаг 10" data-district-input-number-input>
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Увеличить" data-district-input-number-increment>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="district-colors-section">
                    <div class="district-colors-section-title">Границы</div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="color-border" class="leaflet-control-district-colors-label">Цвет</label>
                        <input type="color" id="color-border" value="#444444" class="leaflet-control-district-colors-input" title="Цвет границ полигонов">
                    </div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="border-weight-input" class="leaflet-control-district-colors-label">Ширина</label>
                        <div class="py-1 px-1.5 inline-block bg-layer border border-layer-line rounded-lg" data-district-input-number>
                            <div class="flex items-center gap-x-1.5">
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Уменьшить" data-district-input-number-decrement>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>
                                </button>
                                <input id="border-weight-input" class="p-0 w-6 bg-transparent border-0 text-foreground placeholder:text-muted-foreground-1 text-center focus:ring-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none" style="-moz-appearance: textfield;" type="number" min="1" max="10" value="1" aria-roledescription="Число" title="Ширина границ 1–10 px" data-district-input-number-input>
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Увеличить" data-district-input-number-increment>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="leaflet-control-district-colors-row">
                        <label for="border-opacity-input" class="leaflet-control-district-colors-label">Непрозрачность</label>
                        <div class="py-1 px-1.5 inline-block bg-layer border border-layer-line rounded-lg" data-district-input-number>
                            <div class="flex items-center gap-x-1.5">
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Уменьшить" data-district-input-number-decrement>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>
                                </button>
                                <input id="border-opacity-input" class="p-0 w-6 bg-transparent border-0 text-foreground placeholder:text-muted-foreground-1 text-center focus:ring-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none" style="-moz-appearance: textfield;" type="number" min="0" max="100" value="40" step="10" aria-roledescription="Число" title="Непрозрачность границ 0–100%, шаг 10" data-district-input-number-input>
                                <button type="button" class="size-6 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md bg-layer border border-layer-line text-layer-foreground shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none" tabindex="-1" aria-label="Увеличить" data-district-input-number-increment>
                                    <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="leaflet-control-district-colors-actions-row">
                    <button type="button" id="reset-district-colors-btn" class="py-1.5 px-4 inline-flex items-center gap-x-2 text-sm font-medium rounded-lg bg-layer border border-layer-line text-muted-foreground-1 shadow-2xs hover:bg-layer-hover focus:outline-hidden focus:bg-layer-focus disabled:opacity-50 disabled:pointer-events-none flex-1 justify-center district-colors-reset-btn" title="Вернуть цвета по умолчанию">Сбросить</button>
                    <button type="button" id="save-district-colors-btn" class="py-1.5 px-4 inline-flex items-center gap-x-2 text-sm font-medium rounded-lg shadow-2xs disabled:opacity-50 disabled:pointer-events-none flex-1 justify-center district-colors-save-btn" title="Сохранить настройки на сервер">Сохранить</button>
                </div>
            </div>
        `;
        L.DomEvent.disableClickPropagation(div);
        return div;
    };
    panelControl.addTo(map);

    // Кнопка-шестерёнка для открытия панели
    const toggleControl = L.control({position: 'topright'});
    toggleControl.onAdd = function () {
        const div = L.DomUtil.create('div', 'district-colors-toggle-btn');
        div.innerHTML = `
            <button type="button" class="district-colors-toggle-button" title="Настройки цветов полигонов">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
            </button>
        `;
        L.DomEvent.disableClickPropagation(div);
        div.querySelector('button').addEventListener('click', () => {
            const panel = document.querySelector(DISTRICT_COLORS_PANEL_SELECTOR);
            if (panel) panel.style.display = 'block';
            div.style.display = 'none';
        });
        return div;
    };
    toggleControl.addTo(map);

    // Закрытие панели по клику на ×
    document.addEventListener('click', (e) => {
        if (e.target && e.target.id === 'toggle-district-colors-btn') {
            const panel = document.querySelector(DISTRICT_COLORS_PANEL_SELECTOR);
            const toggleBtn = document.querySelector(DISTRICT_COLORS_TOGGLE_BTN_SELECTOR);
            if (panel && toggleBtn) {
                panel.style.display = 'none';
                toggleBtn.style.display = 'block';
            }
        }
    });

    // Сброс и сохранение по клику на кнопки
    document.addEventListener('click', (e) => {
        if (e.target && e.target.id === 'reset-district-colors-btn') {
            resetDistrictMapColors();
        } else if (e.target && e.target.id === 'save-district-colors-btn') {
            saveDistrictMapColors();
        }
    });
}

/**
 * Сбрасывает цвета полигонов на значения по умолчанию (без сохранения на сервер).
 */
function resetDistrictMapColors() {
    visitedStyle.fillColor = DEFAULT_COLOR_VISITED;
    notVisitedStyle.fillColor = DEFAULT_COLOR_NOT_VISITED;
    visitedStyle.color = DEFAULT_COLOR_BORDER;
    notVisitedStyle.color = DEFAULT_COLOR_BORDER;
    defaultStyle.color = DEFAULT_COLOR_BORDER;
    visitedStyle.weight = DEFAULT_BORDER_WEIGHT;
    notVisitedStyle.weight = DEFAULT_BORDER_WEIGHT;
    defaultStyle.weight = DEFAULT_BORDER_WEIGHT;
    visitedStyle.fillOpacity = DEFAULT_FILL_OPACITY_VISITED / 100;
    notVisitedStyle.fillOpacity = DEFAULT_FILL_OPACITY_NOT_VISITED / 100;
    defaultStyle.fillOpacity = DEFAULT_FILL_OPACITY_NOT_VISITED / 100;
    visitedStyle.opacity = DEFAULT_BORDER_OPACITY / 100;
    notVisitedStyle.opacity = DEFAULT_BORDER_OPACITY / 100;
    defaultStyle.opacity = DEFAULT_BORDER_OPACITY / 100;

    const colorVisitedInput = document.getElementById('color-visited');
    const colorNotVisitedInput = document.getElementById('color-not-visited');
    const colorBorderInput = document.getElementById('color-border');
    const borderWeightInput = document.getElementById('border-weight-input');
    const fillOpacityVisitedInput = document.getElementById('fill-opacity-visited-input');
    const fillOpacityNotVisitedInput = document.getElementById('fill-opacity-not-visited-input');
    const borderOpacityInput = document.getElementById('border-opacity-input');
    if (colorVisitedInput) colorVisitedInput.value = DEFAULT_COLOR_VISITED;
    if (colorNotVisitedInput) colorNotVisitedInput.value = DEFAULT_COLOR_NOT_VISITED;
    if (colorBorderInput) colorBorderInput.value = DEFAULT_COLOR_BORDER;
    if (borderWeightInput) borderWeightInput.value = String(DEFAULT_BORDER_WEIGHT);
    if (fillOpacityVisitedInput) fillOpacityVisitedInput.value = String(DEFAULT_FILL_OPACITY_VISITED);
    if (fillOpacityNotVisitedInput) fillOpacityNotVisitedInput.value = String(DEFAULT_FILL_OPACITY_NOT_VISITED);
    if (borderOpacityInput) borderOpacityInput.value = String(DEFAULT_BORDER_OPACITY);

    applyPolygonColors();
}

/**
 * Загружает сохранённые цвета карты районов с бэкенда и применяет к стилям и пикерам.
 */
async function loadDistrictMapColors() {
    if (!window.IS_AUTHENTICATED || !window.API_MAP_COLORS_URL) return;

    try {
        const response = await fetch(window.API_MAP_COLORS_URL);
        if (!response.ok) return;
        const data = await response.json();

        const colorVisitedInput = document.getElementById('color-visited');
        const colorNotVisitedInput = document.getElementById('color-not-visited');
        const colorBorderInput = document.getElementById('color-border');

        if (data.color_visited != null && data.color_visited !== '' && isValidHexColor(data.color_visited)) {
            visitedStyle.fillColor = data.color_visited;
            if (colorVisitedInput) colorVisitedInput.value = data.color_visited;
        }
        if (data.color_not_visited != null && data.color_not_visited !== '' && isValidHexColor(data.color_not_visited)) {
            notVisitedStyle.fillColor = data.color_not_visited;
            if (colorNotVisitedInput) colorNotVisitedInput.value = data.color_not_visited;
        }
        if (data.color_border != null && data.color_border !== '' && isValidHexColor(data.color_border)) {
            visitedStyle.color = data.color_border;
            notVisitedStyle.color = data.color_border;
            defaultStyle.color = data.color_border;
            if (colorBorderInput) colorBorderInput.value = data.color_border;
        }
        if (data.border_weight != null) {
            const w = Math.max(BORDER_WEIGHT_MIN, Math.min(BORDER_WEIGHT_MAX, Number(data.border_weight)));
            if (Number.isFinite(w)) {
                visitedStyle.weight = w;
                notVisitedStyle.weight = w;
                defaultStyle.weight = w;
                const borderWeightInput = document.getElementById('border-weight-input');
                if (borderWeightInput) borderWeightInput.value = String(Math.round(w));
            }
        }
        const snapOpacityToStep = (o) => Math.round(Math.max(OPACITY_MIN, Math.min(OPACITY_MAX, o)) / OPACITY_STEP) * OPACITY_STEP;
        if (data.fill_opacity_visited != null) {
            const o = Math.max(OPACITY_MIN, Math.min(OPACITY_MAX, Number(data.fill_opacity_visited)));
            if (Number.isFinite(o)) {
                const stepped = snapOpacityToStep(o);
                visitedStyle.fillOpacity = stepped / 100;
                const el = document.getElementById('fill-opacity-visited-input');
                if (el) el.value = String(stepped);
            }
        }
        if (data.fill_opacity_not_visited != null) {
            const o = Math.max(OPACITY_MIN, Math.min(OPACITY_MAX, Number(data.fill_opacity_not_visited)));
            if (Number.isFinite(o)) {
                const stepped = snapOpacityToStep(o);
                notVisitedStyle.fillOpacity = stepped / 100;
                defaultStyle.fillOpacity = stepped / 100;
                const el = document.getElementById('fill-opacity-not-visited-input');
                if (el) el.value = String(stepped);
            }
        }
        if (data.border_opacity != null) {
            const o = Math.max(OPACITY_MIN, Math.min(OPACITY_MAX, Number(data.border_opacity)));
            if (Number.isFinite(o)) {
                const stepped = snapOpacityToStep(o);
                visitedStyle.opacity = stepped / 100;
                notVisitedStyle.opacity = stepped / 100;
                defaultStyle.opacity = stepped / 100;
                const el = document.getElementById('border-opacity-input');
                if (el) el.value = String(stepped);
            }
        }
    } catch (err) {
        console.warn('Не удалось загрузить настройки цветов карты районов:', err);
    }
}

/**
 * Отправляет текущие настройки цветов карты районов на бэкенд.
 * Показывает toast об успехе или ошибке.
 */
function saveDistrictMapColors() {
    if (!window.IS_AUTHENTICATED || !window.API_MAP_COLORS_SAVE_URL) return;

    const body = {
        color_visited: visitedStyle.fillColor,
        color_not_visited: notVisitedStyle.fillColor,
        color_border: visitedStyle.color,
        border_weight: visitedStyle.weight,
        fill_opacity_visited: Math.round(visitedStyle.fillOpacity * 100),
        fill_opacity_not_visited: Math.round(notVisitedStyle.fillOpacity * 100),
        border_opacity: Math.round(visitedStyle.opacity * 100),
    };
    fetch(window.API_MAP_COLORS_SAVE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(body),
    })
        .then((response) => {
            if (response.ok) {
                showSuccessToast('Успешно', 'Настройки цветов карты сохранены.');
            } else {
                showDangerToast('Ошибка', 'Не удалось сохранить настройки. Попробуйте позже.');
            }
        })
        .catch((err) => {
            console.warn('Не удалось сохранить цвета карты районов:', err);
            showDangerToast('Ошибка', 'Не удалось сохранить настройки. Проверьте соединение.');
        });
}

/**
 * Подключает обработчики color picker для цветов посещённых/непосещённых районов и границ.
 * На input — throttle перерисовки; на change — немедленная перерисовка. Сохранение на сервер — по кнопке «Сохранить».
 */
function initColorPickers() {
    const colorVisitedInput = document.getElementById('color-visited');
    const colorNotVisitedInput = document.getElementById('color-not-visited');
    const colorBorderInput = document.getElementById('color-border');
    const borderWeightInput = document.getElementById('border-weight-input');
    const borderWeightContainer = borderWeightInput
        ? borderWeightInput.closest('[data-district-input-number]')
        : null;
    const borderWeightDecrement = borderWeightContainer
        ? borderWeightContainer.querySelector('[data-district-input-number-decrement]')
        : null;
    const borderWeightIncrement = borderWeightContainer
        ? borderWeightContainer.querySelector('[data-district-input-number-increment]')
        : null;
    if (!colorVisitedInput || !colorNotVisitedInput || !colorBorderInput || !borderWeightInput) return;

    colorVisitedInput.value = visitedStyle.fillColor;
    colorNotVisitedInput.value = notVisitedStyle.fillColor;
    colorBorderInput.value = visitedStyle.color;
    borderWeightInput.value = String(visitedStyle.weight);

    colorVisitedInput.addEventListener('input', () => {
        visitedStyle.fillColor = colorVisitedInput.value;
        applyPolygonColorsThrottled();
    });
    colorVisitedInput.addEventListener('change', () => {
        visitedStyle.fillColor = colorVisitedInput.value;
        applyPolygonColors();
    });

    colorNotVisitedInput.addEventListener('input', () => {
        notVisitedStyle.fillColor = colorNotVisitedInput.value;
        applyPolygonColorsThrottled();
    });
    colorNotVisitedInput.addEventListener('change', () => {
        notVisitedStyle.fillColor = colorNotVisitedInput.value;
        applyPolygonColors();
    });

    colorBorderInput.addEventListener('input', () => {
        visitedStyle.color = colorBorderInput.value;
        notVisitedStyle.color = colorBorderInput.value;
        defaultStyle.color = colorBorderInput.value;
        applyPolygonColorsThrottled();
    });
    colorBorderInput.addEventListener('change', () => {
        visitedStyle.color = colorBorderInput.value;
        notVisitedStyle.color = colorBorderInput.value;
        defaultStyle.color = colorBorderInput.value;
        applyPolygonColors();
    });

    const applyBorderWeight = (value) => {
        const w = Math.max(BORDER_WEIGHT_MIN, Math.min(BORDER_WEIGHT_MAX, Number(value)));
        if (!Number.isFinite(w)) return;
        const rounded = Math.round(w);
        visitedStyle.weight = rounded;
        notVisitedStyle.weight = rounded;
        defaultStyle.weight = rounded;
        borderWeightInput.value = String(rounded);
    };

    if (borderWeightDecrement) {
        borderWeightDecrement.addEventListener('click', () => {
            const current = Math.max(BORDER_WEIGHT_MIN, Math.min(BORDER_WEIGHT_MAX, Number(borderWeightInput.value) || 1));
            const next = Math.max(BORDER_WEIGHT_MIN, current - 1);
            applyBorderWeight(next);
            applyPolygonColors();
        });
    }
    if (borderWeightIncrement) {
        borderWeightIncrement.addEventListener('click', () => {
            const current = Math.max(BORDER_WEIGHT_MIN, Math.min(BORDER_WEIGHT_MAX, Number(borderWeightInput.value) || 1));
            const next = Math.min(BORDER_WEIGHT_MAX, current + 1);
            applyBorderWeight(next);
            applyPolygonColors();
        });
    }
    borderWeightInput.addEventListener('input', () => {
        applyBorderWeight(borderWeightInput.value);
        applyPolygonColorsThrottled();
    });
    borderWeightInput.addEventListener('change', () => {
        applyBorderWeight(borderWeightInput.value);
        applyPolygonColors();
    });

    // Непрозрачность: заливка посещённых, заливка непосещённых, границы
    const fillOpacityVisitedInput = document.getElementById('fill-opacity-visited-input');
    const fillOpacityNotVisitedInput = document.getElementById('fill-opacity-not-visited-input');
    const borderOpacityInput = document.getElementById('border-opacity-input');
    const opacityToStep = (o) => Math.round((o * 100) / OPACITY_STEP) * OPACITY_STEP;
    if (fillOpacityVisitedInput) fillOpacityVisitedInput.value = String(opacityToStep(visitedStyle.fillOpacity));
    if (fillOpacityNotVisitedInput) fillOpacityNotVisitedInput.value = String(opacityToStep(notVisitedStyle.fillOpacity));
    if (borderOpacityInput) borderOpacityInput.value = String(opacityToStep(visitedStyle.opacity));

    /** Округляет значение прозрачности до шага 10 (0, 10, 20, …, 100). */
    const clampOpacityToStep = (v) => {
        const n = Number(v);
        if (!Number.isFinite(n)) return null;
        const clamped = Math.max(OPACITY_MIN, Math.min(OPACITY_MAX, n));
        const stepped = Math.round(clamped / OPACITY_STEP) * OPACITY_STEP;
        return Math.max(OPACITY_MIN, Math.min(OPACITY_MAX, stepped));
    };

    const bindOpacityControls = (inputEl, setValue) => {
        if (!inputEl) return;
        const container = inputEl.closest('[data-district-input-number]');
        const dec = container?.querySelector('[data-district-input-number-decrement]');
        const inc = container?.querySelector('[data-district-input-number-increment]');
        const apply = (value) => {
            const n = clampOpacityToStep(value);
            if (n === null) return;
            setValue(n);
            inputEl.value = String(n);
        };
        if (dec) {
            dec.addEventListener('click', () => {
                const cur = clampOpacityToStep(inputEl.value) ?? OPACITY_MIN;
                apply(Math.max(OPACITY_MIN, cur - OPACITY_STEP));
                applyPolygonColors();
            });
        }
        if (inc) {
            inc.addEventListener('click', () => {
                const cur = clampOpacityToStep(inputEl.value) ?? OPACITY_MIN;
                apply(Math.min(OPACITY_MAX, cur + OPACITY_STEP));
                applyPolygonColors();
            });
        }
        inputEl.addEventListener('input', () => {
            apply(inputEl.value);
            applyPolygonColorsThrottled();
        });
        inputEl.addEventListener('change', () => {
            apply(inputEl.value);
            applyPolygonColors();
        });
    };

    bindOpacityControls(fillOpacityVisitedInput, (n) => {
        visitedStyle.fillOpacity = n / 100;
    });

    bindOpacityControls(fillOpacityNotVisitedInput, (n) => {
        notVisitedStyle.fillOpacity = n / 100;
        defaultStyle.fillOpacity = n / 100;
    });

    bindOpacityControls(borderOpacityInput, (n) => {
        visitedStyle.opacity = n / 100;
        notVisitedStyle.opacity = n / 100;
        defaultStyle.opacity = n / 100;
    });
}

/**
 * Загружает список городов с районами для селектора.
 * Инициализирует Preline UI компонент HSSelect с поиском.
 */
async function loadCitiesForSelect() {
    const select = document.getElementById('city-select');
    if (!select) return;

    try {
        const response = await fetch(window.API_CITIES_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const cities = await response.json();
        
        // Очищаем селектор
        select.innerHTML = '';
        
        // Добавляем опцию по умолчанию
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Выберите город...';
        select.appendChild(defaultOption);
        
        // Добавляем города
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city.id;
            option.textContent = city.title;
            if (parseInt(city.id) === parseInt(window.CITY_ID)) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        // Preline UI автоматически обновит компонент при изменении опций в DOM
        // Если компонент уже был инициализирован, переинициализируем его
        const hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance('#city-select') : null;
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
        }
        
        // Переинициализируем компонент с новыми опциями
        if (window.HSSelect) {
            try {
                new window.HSSelect('#city-select');
            } catch (e) {
                // Если не получилось, используем autoInit
                if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                    window.HSStaticMethods.autoInit();
                }
            }
        }
        
        // Обработчик изменения города (используем делегирование событий, чтобы избежать множественных обработчиков)
        // Удаляем старый обработчик, если он был добавлен ранее
        const oldHandler = select._changeHandler;
        if (oldHandler) {
            select.removeEventListener('change', oldHandler);
        }
        
        // Создаём новый обработчик
        const changeHandler = (e) => {
            const cityId = parseInt(e.target.value);
            if (cityId) {
                window.location.href = `/city/districts/${cityId}/map`;
            }
        };
        
        // Сохраняем ссылку на обработчик для возможности удаления в будущем
        select._changeHandler = changeHandler;
        select.addEventListener('change', changeHandler);
    } catch (error) {
        console.error('Ошибка загрузки списка городов:', error);
    }
}

/**
 * Загружает данные о районах и GeoJSON полигоны параллельно.
 */
async function loadDistrictsData(cityId, countryCode, cityName, regionCode) {
    const loadControl = addLoadControl(map, 'Загружаю данные о районах...');
    
    try {
        // Формируем тело запроса для GeoJSON
        const geoJsonBody = {
            country_code: countryCode,
            city_name: cityName,
            region_code: regionCode,
        };
        
        // Параллельная загрузка данных о районах и GeoJSON
        const [districtsResponse, geoJsonResponse] = await Promise.all([
            fetch(`${window.API_DISTRICTS_URL}`),
            fetch(`${window.URL_GEO_POLYGONS}/city-district/hq`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(geoJsonBody),
            }),
        ]);
        
        map.removeControl(loadControl);
        
        // Обработка ответа с данными о районах
        if (!districtsResponse.ok) {
            if (districtsResponse.status === 404) {
                addErrorControl(map, 'Для этого города нет районов в базе данных');
                return;
            }
            throw new Error(`HTTP error! status: ${districtsResponse.status}`);
        }
        
        const districts = await districtsResponse.json();
        
        // Создаём Map для быстрого поиска по названию
        districtsData.clear();
        districts.forEach(district => {
            districtsData.set(district.title, {
                id: district.id,
                is_visited: district.is_visited || false,
                area: district.area,
                population: district.population,
            });
        });
        
        // Обработка ответа с GeoJSON
        if (!geoJsonResponse.ok) {
            if (geoJsonResponse.status === 404) {
                addErrorControl(map, 'Для этого города нет полигонов районов');
                return;
            }
            throw new Error(`HTTP error! status: ${geoJsonResponse.status}`);
        }
        
        const geoJsonData = await geoJsonResponse.json();
        cachedGeoJson = geoJsonData;
        
        // Отображаем полигоны на карте
        displayDistrictsOnMap(geoJsonData, districtsData);
        
        // Обновляем бейджик со статистикой
        updateStatsBadge();
        
        // Центрируем карту по полигонам
        if (geoJsonLayers.length > 0) {
            const group = new L.featureGroup(geoJsonLayers);
            map.fitBounds(group.getBounds());
        }
        
    } catch (error) {
        map.removeControl(loadControl);
        console.error('Ошибка загрузки данных:', error);
        addErrorControl(map, 'Произошла ошибка при загрузке данных о районах');
        showDangerToast('Ошибка соединения с сервером', 'Не получилось загрузить данные о районах.');
    }
}

/**
 * Отображает полигоны районов на карте.
 */
function displayDistrictsOnMap(geoJsonData, districtsDataMap) {
    // Очищаем предыдущие слои
    geoJsonLayers.forEach(layer => {
        map.removeLayer(layer);
    });
    geoJsonLayers = [];
    
    // Проверяем, что пришло: массив FeatureCollection или один FeatureCollection
    const featureCollections = Array.isArray(geoJsonData) ? geoJsonData : [geoJsonData];
    
    featureCollections.forEach(featureCollection => {
        // Проверяем, что это FeatureCollection
        if (featureCollection.type !== 'FeatureCollection' || !featureCollection.features) {
            console.warn('Неверный формат GeoJSON:', featureCollection);
            return;
        }
        
        // Обрабатываем каждый feature в FeatureCollection
        featureCollection.features.forEach(feature => {
            // Получаем название района из properties.feature
            const districtName = feature.properties?.name || feature.properties?.title || '';
            const districtInfo = districtsDataMap.get(districtName);
            
            // Отладочная информация (можно удалить после проверки)
            if (!districtInfo && districtName) {
                console.log(`Район "${districtName}" не найден в данных БД. Доступные районы:`, Array.from(districtsDataMap.keys()));
            }
            
            // Определяем стиль в зависимости от того, посещён ли район
            const style = districtInfo?.is_visited ? visitedStyle : (districtInfo ? notVisitedStyle : defaultStyle);
            
            // Создаём слой GeoJSON для отдельного feature
            const layer = L.geoJSON(feature, {
                style: style,
            });
            
            // Добавляем popup при клике
            layer.bindPopup(() => {
                return createPopupContent(districtName, districtInfo);
            }, {maxWidth: 400, minWidth: 280});
            
            // Инициализируем Preline UI для элементов в popup после его открытия
            layer.on('popupopen', function() {
                if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                    window.HSStaticMethods.autoInit();
                }
            });
            
            // Добавляем tooltip при наведении
            const tooltip = layer.bindTooltip(districtName, {
                direction: 'top',
                sticky: true
            });
            
            // Предотвращаем перемещение tooltip в центр при клике
            const originalUpdatePosition = tooltip.updatePosition;
            let isClickInProgress = false;
            
            tooltip.updatePosition = function(e) {
                if (isClickInProgress) return;
                return originalUpdatePosition.call(this, e);
            };
            
            // Скрываем tooltip при нажатии мыши
            layer.on('mousedown', function () {
                isClickInProgress = true;
                const tooltip = this.getTooltip();
                if (tooltip) {
                    tooltip.setOpacity(0.0);
                    if (tooltip._container) tooltip._container.style.display = 'none';
                }
            });
            
            layer.on('mouseup', function () {
                setTimeout(() => { isClickInProgress = false; }, 100);
            });
            
            // Показываем tooltip при наведении
            layer.on('mouseover', function () {
                const tooltip = this.getTooltip();
                if (tooltip && !this.isPopupOpen()) {
                    if (tooltip._container) tooltip._container.style.display = '';
                    tooltip.setOpacity(0.9);
                }
            });
            
            // Скрываем tooltip при уходе курсора или открытии/закрытии popup
            layer.on('mouseout popupopen popupclose', function (e) {
                const tooltip = this.getTooltip();
                if (tooltip) {
                    tooltip.setOpacity(0.0);
                    // Для popup всегда скрываем container, для mouseout - только если popup не открыт
                    if (tooltip._container && (e.type === 'popupopen' || e.type === 'popupclose' || !this.isPopupOpen())) {
                        tooltip._container.style.display = 'none';
                    }
                }
            });
            
            layer.addTo(map);
            geoJsonLayers.push(layer);
        });
    });
}

/**
 * Создаёт содержимое popup для района.
 */
function createPopupContent(districtName, districtInfo) {
    let content = '<div class="px-1.5 py-1.5 min-w-[280px] max-w-[400px]">';
    
    // Заголовок (стиль аналогичный popup для городов)
    content += `<div class="mb-2 pb-1 border-b border-gray-200 dark:border-neutral-700">`;
    content += `<h3 class="text-base font-semibold text-gray-900 dark:text-white mb-0">${districtName}</h3>`;
    content += `</div>`;
    
    if (districtInfo) {
        // Информация о районе (с иконками и бейджиками, как в popup для городов)
        content += '<div class="space-y-1.5 text-sm">';
        
        if (districtInfo.area) {
            content += `<div class="flex items-center justify-between gap-2">`;
            content += `<div class="flex items-center gap-2">`;
            content += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>`;
            content += `<span class="text-gray-500 dark:text-neutral-400">Площадь:</span>`;
            content += `</div>`;
            content += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${districtInfo.area} км²</span>`;
            content += `</div>`;
        }
        
        if (districtInfo.population) {
            content += `<div class="flex items-center justify-between gap-2">`;
            content += `<div class="flex items-center gap-2">`;
            content += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`;
            content += `<span class="text-gray-500 dark:text-neutral-400">Население:</span>`;
            content += `</div>`;
            content += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-500/10 dark:text-purple-400">${districtInfo.population.toLocaleString()}</span>`;
            content += `</div>`;
        }
        
        if (districtInfo.is_visited) {
            content += `<div class="flex items-center justify-between gap-2">`;
            content += `<div class="flex items-center gap-2">`;
            content += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
            content += `<span class="text-gray-500 dark:text-neutral-400">Статус:</span>`;
            content += `</div>`;
            content += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-400">Посещён</span>`;
            content += `</div>`;
        }
        
        content += '</div>';
        
        // Форма отметки посещения для авторизованных пользователей
        if (window.IS_AUTHENTICATED) {
            content += '<div class="mt-2 pt-2 border-t border-gray-200 dark:border-neutral-700">';
            if (districtInfo.is_visited) {
                // Если район посещён, показываем ссылку для удаления
                content += `<a href="#" id="delete-visit-link-${districtInfo.id}" class="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors">Удалить посещение</a>`;
            } else {
                // Если район не посещён, показываем форму для отметки
                content += `<form id="visit-district-form-${districtInfo.id}">`;
                content += `<input type="hidden" name="city_district_id" value="${districtInfo.id}">`;
                content += `<button type="submit" class="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors">`;
                content += 'Отметить как посещённый';
                content += `</button>`;
                content += `</form>`;
            }
            content += '</div>';
        }
    } else {
        content += '<div class="space-y-1.5 text-sm">';
        content += `<div class="text-sm">`;
        content += `<span class="text-gray-900 dark:text-white">Информация о районе отсутствует</span>`;
        content += `</div>`;
        content += '</div>';
    }
    
    content += '</div>';
    return content;
}

/**
 * Обновляет текст бейджика со статистикой посещённых районов.
 */
function updateStatsBadge() {
    if (!window.IS_AUTHENTICATED) {
        return;
    }

    const badgeElement = document.querySelector('#section-stats .stat-badge');
    if (!badgeElement) {
        return;
    }

    // Подсчитываем количество посещённых районов
    let qtyOfVisitedDistricts = 0;
    let qtyOfDistricts = 0;
    
    districtsData.forEach((districtInfo) => {
        qtyOfDistricts++;
        if (districtInfo.is_visited) {
            qtyOfVisitedDistricts++;
        }
    });

    if (qtyOfDistricts > 0) {
        const word = pluralize(qtyOfVisitedDistricts, 'район', 'района', 'районов');
        badgeElement.innerHTML = `
            <span class="stat-badge-dot"></span>
            Посещено <strong>${qtyOfVisitedDistricts}</strong> ${word} из ${qtyOfDistricts}
        `;
    } else {
        badgeElement.innerHTML = `
            <span class="stat-badge-dot"></span>
            Нет информации о районах
        `;
    }
}

/**
 * Обрабатывает отправку формы отметки посещения.
 */
function handleVisitFormSubmit(event, districtId, districtName) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        city_district_id: parseInt(formData.get('city_district_id')),
    };
    
    fetch(window.API_VISIT_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    const errorMessage = err.detail || err.city_district_id?.[0] || 'Ошибка при сохранении';
                    throw new Error(errorMessage);
                });
            }
            return response.json();
        })
        .then(async result => {
            // Перезагружаем данные о районах для обновления статуса is_visited
            if (window.CITY_ID && window.COUNTRY_CODE && window.CITY_NAME) {
                const districtsResponse = await fetch(`${window.API_DISTRICTS_URL}`);
                if (districtsResponse.ok) {
                    const districts = await districtsResponse.json();
                    districtsData.clear();
                    districts.forEach(district => {
                        districtsData.set(district.title, {
                            id: district.id,
                            is_visited: district.is_visited || false,
                            area: district.area,
                            population: district.population,
                        });
                    });
                    
                    // Перерисовываем полигоны с обновлёнными стилями
                    if (cachedGeoJson) {
                        displayDistrictsOnMap(cachedGeoJson, districtsData);
                    }
                    
                    // Обновляем бейджик со статистикой
                    updateStatsBadge();
                }
            }
            
            // Показываем уведомление об успехе
            const message = `Район <span class="font-semibold">${districtName}</span> успешно отмечен как посещённый`;
            showSuccessToast('Успешно', message);
            
            // Закрываем popup
            map.closePopup();
        })
        .catch(error => {
            console.error('Ошибка при сохранении посещения:', error);
            alert('Ошибка при сохранении: ' + error.message);
        });
}

/**
 * Обрабатывает удаление посещения района.
 */
async function handleDeleteVisit(districtId, districtName) {
    if (!window.API_VISIT_DELETE_URL) {
        console.error('URL для удаления посещения не определён');
        return;
    }

    const data = {
        city_district_id: districtId,
    };

    try {
        const response = await fetch(window.API_VISIT_DELETE_URL, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const err = await response.json();
            const errorMessage = err.detail || 'Ошибка при удалении посещения';
            throw new Error(errorMessage);
        }

        // Перезагружаем данные о районах для обновления статуса is_visited
        if (window.CITY_ID && window.COUNTRY_CODE && window.CITY_NAME) {
            const districtsResponse = await fetch(`${window.API_DISTRICTS_URL}`);
            if (districtsResponse.ok) {
                const districts = await districtsResponse.json();
                districtsData.clear();
                districts.forEach(district => {
                    districtsData.set(district.title, {
                        id: district.id,
                        is_visited: district.is_visited || false,
                        area: district.area,
                        population: district.population,
                    });
                });

                // Перерисовываем полигоны с обновлёнными стилями
                if (cachedGeoJson) {
                    displayDistrictsOnMap(cachedGeoJson, districtsData);
                }
                
                // Обновляем бейджик со статистикой
                updateStatsBadge();
            }
        }

        // Показываем уведомление об успехе
        const message = `Посещение района <span class="font-semibold">${districtName}</span> успешно удалено`;
        showSuccessToast('Успешно', message);

        // Закрываем popup
        map.closePopup();
    } catch (error) {
        console.error('Ошибка при удалении посещения:', error);
        alert('Ошибка при удалении: ' + error.message);
    }
}

/**
 * Инициализация карты при загрузке страницы.
 */
async function initDistrictsMap() {
    map = create_map();
    window.MG_MAIN_MAP = map;

    // Контрол выбора цветов полигонов на карте (посещённые / не посещённые)
    addColorPickersControl(map);

    // Загружаем список городов для селектора
    await loadCitiesForSelect();

    // Подключаем обработчики color picker и загружаем сохранённые цвета
    initColorPickers();
    await loadDistrictMapColors();

    // Загружаем данные о районах текущего города
    if (window.CITY_ID && window.COUNTRY_CODE && window.CITY_NAME) {
        currentCityId = window.CITY_ID;
        await loadDistrictsData(window.CITY_ID, window.COUNTRY_CODE, window.CITY_NAME, window.REGION_CODE);
    }
    
    // Обработчик отправки форм посещения (делегирование событий)
    document.addEventListener('submit', (event) => {
        const form = event.target;
        if (form.id && form.id.startsWith('visit-district-form-')) {
            const districtId = parseInt(form.querySelector('input[name="city_district_id"]').value);
            const districtName = Array.from(districtsData.keys()).find(name => {
                const info = districtsData.get(name);
                return info && info.id === districtId;
            });
            if (districtName) {
                handleVisitFormSubmit(event, districtId, districtName);
            }
        }
    });

    // Обработчик клика на ссылки удаления посещения (делегирование событий)
    document.addEventListener('click', (event) => {
        const target = event.target;
        if (target.id && target.id.startsWith('delete-visit-link-')) {
            event.preventDefault();
            const districtId = parseInt(target.id.replace('delete-visit-link-', ''));
            const districtName = Array.from(districtsData.keys()).find(name => {
                const info = districtsData.get(name);
                return info && info.id === districtId;
            });
            if (districtName) {
                handleDeleteVisit(districtId, districtName);
            }
        }
    });
}

// Инициализация при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDistrictsMap);
} else {
    initDistrictsMap();
}
