/**
 * Реализует функции для создания объекта карты.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import * as L from 'leaflet';
import 'leaflet-fullscreen';
import {SimpleMapScreenshoter} from 'leaflet-simple-map-screenshoter';

/**
 * Создаёт и возвращает объект карты с подложкой (OpenStreetMap) и кнопками зума,
 * полноэкранного режима, либо скриншота, либо (страница «карта городов») кнопки «Помощь».
 * @param {{ mapPageHelp?: boolean }} [options]
 */
let downloadedExternalBorder = undefined;
let downloadedInternalBorder = undefined;
let externalBorder = undefined;
let internalBorder = [];

const fillOpacity = 0.1;
const fillColor = '#6382ff';
const strokeColor = '#0033ff';
const strokeOpacity = 0.3;
const strokeWidth = 2;

const myStyle = {
    fillOpacity: fillOpacity,
    fillColor: fillColor,
    weight: strokeWidth,
    color: strokeColor,
    opacity: strokeOpacity
};

export function create_map(options = {}) {
    const mapPageHelp = options.mapPageHelp === true;
    const map = L.map('map', {
        attributionControl: false,
        zoomControl: false
    });

    add_attribution(map);
    add_zoom_control(map);
    add_fullscreen_control(map);
    if (mapPageHelp) {
        addMapPageHelpControl(map);
    } else {
        add_screenshot_control(map);
    }

    return map
}

/**
 * Добавляет кнопку полноэкранного просмотра.
 * @param map Объект карты, на которую нужно добавить кнопки.
 */
function add_fullscreen_control(map) {
    map.addControl(new L.Control.Fullscreen({
        title: {
            'false': 'Полноэкранный режим',
            'true': 'Выйти из полноэкранного режима'
        }
    }));
}


/**
 * Добавляет кнопки приближения и отдаления карты.
 * @param map Объект карты, на которую нужно добавить кнопки.
 */
function add_zoom_control(map) {
    const zoomControl = L.control.zoom({
        zoomInTitle: 'Приблизить карту',
        zoomOutTitle: 'Отдалить карту'
    });
    zoomControl.addTo(map);
}

/**
 * Добавляет в правый нижний угол указание об использовании карт OopenStreetMap и их лицензии.
 * @param map Объект карты, на который нужно добавить информацию.
 */
function add_attribution(map) {
    const myAttrControl = L.control.attribution().addTo(map);
    myAttrControl.setPrefix('');
    L.tileLayer(window.TILE_LAYER, {
        maxZoom: 19,
        attribution: 'Используются карты &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/">ODbL.</a>'
    }).addTo(map);
}

/**
 * Добавляет кнопку создания скриншота карты.
 * @param map Объект карты, на которую нужно добавить кнопку.
 */
function add_screenshot_control(map) {
    const screenshotControl = new SimpleMapScreenshoter({
        hideElementsWithSelectors: ['.leaflet-control-container'],
        preventDownload: false,
        hidden: false,
        mimeType: 'image/png',
        caption: null,
        position: 'topleft',
        screenName: 'MoiGoroda',
    });
    screenshotControl.addTo(map);
    
    // Добавляем подсказку для кнопки скриншота
    map.whenReady(() => {
        setTimeout(() => {
            const screenshotBtn = document.querySelector('#map .leaflet-control-simpleMapScreenshoter-btn');
            if (screenshotBtn) {
                screenshotBtn.setAttribute('title', 'Создать скриншот карты');
            }
        }, 100);
    });
}

/**
 * Кнопка «Помощь» (иконка, как custom-control-for-map) вместо скриншота — только страница карты городов.
 * Открывает #helpModal через Preline HSOverlay.
 */
function addMapPageHelpControl(map) {
    const Help = L.Control.extend({
        onAdd: function () {
            const wrap = L.DomUtil.create('div', 'leaflet-map-page-help');
            const el = L.DomUtil.create('div', 'custom-control-for-map', wrap);
            el.id = 'btn_help';
            el.setAttribute('role', 'button');
            el.setAttribute('tabindex', '0');
            el.title = 'Открыть подробное описание функций страницы';
            el.setAttribute('aria-label', el.title);
            el.innerHTML =
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" class="control-icon control-icon--solid" fill="currentColor" aria-hidden="true">' +
                '<path d="M528 320C528 205.1 434.9 112 320 112C205.1 112 112 205.1 112 320C112 434.9 205.1 528 320 528C434.9 528 528 434.9 528 320zM64 320C64 178.6 178.6 64 320 64C461.4 64 576 178.6 576 320C576 461.4 461.4 576 320 576C178.6 576 64 461.4 64 320zM320 240C302.3 240 288 254.3 288 272C288 285.3 277.3 296 264 296C250.7 296 240 285.3 240 272C240 227.8 275.8 192 320 192C364.2 192 400 227.8 400 272C400 319.2 364 339.2 344 346.5L344 350.3C344 363.6 333.3 374.3 320 374.3C306.7 374.3 296 363.6 296 350.3L296 342.2C296 321.7 310.8 307 326.1 302C332.5 299.9 339.3 296.5 344.3 291.7C348.6 287.5 352 281.7 352 272.1C352 254.4 337.7 240.1 320 240.1zM288 432C288 414.3 302.3 400 320 400C337.7 400 352 414.3 352 432C352 449.7 337.7 464 320 464C302.3 464 288 449.7 288 432z"/>' +
                '</svg>';
            L.DomEvent.disableClickPropagation(wrap);
            L.DomEvent.disableScrollPropagation(wrap);
            const open = () => {
                void import('preline').then((m) => {
                    if (m.HSOverlay && typeof m.HSOverlay.open === 'function') {
                        m.HSOverlay.open('#helpModal');
                    }
                });
            };
            L.DomEvent.on(el, 'click', (e) => {
                L.DomEvent.stop(e);
                open();
            });
            L.DomEvent.on(el, 'keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    L.DomEvent.stop(e);
                    open();
                }
            });
            return wrap;
        }
    });
    (new Help({ position: 'topleft' })).addTo(map);
}

export function addExternalBorderControl(map, countryCode) {
    const external_border = new L.Control({
        position: 'topright',
    });
    const container = L.DomUtil.create('div', 'custom-control-for-map');
    container.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="control-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>';

    // Если страна не указана - делаем контрол неактивным
    if (countryCode === null || countryCode === undefined) {
        external_border.onAdd = function (map) {
            container.title = 'Выберите страну, чтобы загрузить её границы';
            container.style.opacity = '0.5'; // Визуально — неактивный

            return container;
        };
        external_border.addTo(map);
        return;
    }

    external_border.onAdd = function (map) {
        container.title = 'Отобразить внешние границы страны';

        container.addEventListener('click', () => {
            if (downloadedExternalBorder === undefined) {
                const load = addLoadControl(map, 'Загружаю внешние границы страны...');

                fetch(`https://geo-polygons.ru/country/hq/${countryCode}`)
                    .then(response => {
                        if (!response.ok) {
                            map.removeControl(load);
                            addErrorControl(map, 'Произошла ошибка при загрузке внешних границ страны');
                            throw new Error('Ошибка при получении внешних границ страны')
                        }
                        return response.json();
                    })
                    .then(polygon => {
                        removeBorderFromMap(externalBorder, internalBorder);

                        externalBorder = L.geoJSON(polygon, {
                            style: myStyle,
                        });
                        externalBorder.addTo(map);
                        downloadedExternalBorder = polygon;
                        map.removeControl(load);
                    })
            } else {
                removeBorderFromMap(externalBorder, internalBorder);

                externalBorder = L.geoJSON(downloadedExternalBorder, {
                    style: myStyle,
                });
                externalBorder.addTo(map);
            }
        });
        return container;
    }
    external_border.addTo(map);
}

export function addInternalBorderControl(map, countryCode) {
    const external_border = new L.Control({
        position: 'topright'
    });
    const container = L.DomUtil.create('div', 'custom-control-for-map')
    container.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="control-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>';

    // Если страна не указана - делаем контрол неактивным
    if (countryCode === null || countryCode === undefined) {
        external_border.onAdd = function (map) {
            container.title = 'Выберите страну, чтобы загрузить границы её регионов';
            container.style.opacity = '0.5'; // Визуально — неактивный

            return container;
        };
        external_border.addTo(map);
        return;
    }

    external_border.onAdd = function (map) {
        container.title = 'Отобразить границы регионов страны';

        container.addEventListener('click', () => {
            if (downloadedInternalBorder === undefined) {
                const load = addLoadControl(map, 'Загружаю границы регионов страны...');

                fetch(`${URL_GEO_POLYGONS}/region/lq/${countryCode}/all`)
                    .then(response => {
                        if (!response.ok) {
                            map.removeControl(load);

                            if (response.status === 404) {
                                addErrorControl(map, 'В выбранной Вами стране нет территориального деления на регионы');
                                throw new Error('В выбранной Вами стране нет территориального деления на регионы');
                            }
                                addErrorControl(map, 'Произошла ошибка при загрузке границ регионов страны');
                            throw new Error('Ошибка при получении границ регионов страны');
                        }
                        return response.json();
                    })
                    .then(polygons => {
                        removeBorderFromMap(externalBorder, internalBorder);

                        polygons.forEach(polygon => {
                            const layer = L.geoJSON(polygon, {
                                style: myStyle,
                            }).addTo(map);
                            internalBorder.push(layer);
                        });
                        downloadedInternalBorder = polygons;

                        map.removeControl(load);
                    })
            } else {
                removeBorderFromMap(externalBorder, internalBorder);

                downloadedInternalBorder.forEach(polygon => {
                    const layer = L.geoJSON(polygon, {
                        style: myStyle,
                    }).addTo(map);
                    internalBorder.push(layer);
                });
            }
        });
        return container;
    }
    external_border.addTo(map);
}

function removeBorderFromMap(externalBorder, internalBorder) {
    if (externalBorder !== undefined) {
        externalBorder.clearLayers();
    }
    if (internalBorder !== undefined) {
        internalBorder.forEach(layer => {
            layer.clearLayers();
        });
    }
}

/**
 * Создаёт на карте map панель с информацией о том, что идёт загрузка полигонов.
 */
export function addLoadControl(map, label) {
    const load = L.control({position: 'bottomright'});

    load.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'load');
        this.update();
        return this._div;
    };
    load.update = function (props) {
        this._div.innerHTML = '<div class="flex items-center justify-center gap-2">'
            + '<div class="inline-block size-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent" role="status">'
            + `<span class="sr-only">Загрузка...</span></div><div>${label}</div></div>`;
    };
    load.addTo(map);

    return load
}

/**
 * Создаёт на карте map панель с информацией о том, что произошла ошибка при загрузке полигонов.
 */
export function addErrorControl(map, label) {
    const error = L.control({position: 'bottomright'});

    error.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'error');
        this.update();
        return this._div;
    };
    error.update = function (props) {
        this._div.innerHTML = `<div>${label}</div>`;
    };
    error.addTo(map);

    setTimeout(() => {
        map.removeControl(error);
    }, 3000)

    return error
}