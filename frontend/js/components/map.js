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
 * Создаёт и возвращает объект карты с подложкой в виде карты OpenStreetMap
 * и кнопками увеличения/уменьшения масштаба, полноэкранного режима и создания скриншота.
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

export function create_map() {
    const map = L.map('map', {
        attributionControl: false,
        zoomControl: false
    });

    add_attribution(map);
    add_zoom_control(map);
    add_fullscreen_control(map);
    add_screenshot_control(map);

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
        zoomInTitle: 'Нажмите, чтобы приблизить карту',
        zoomOutTitle: 'Нажмите, чтобы отдалить карту'
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
    new SimpleMapScreenshoter({
        hideElementsWithSelectors: ['.leaflet-control-container'],
        preventDownload: false,
        hidden: false,
        mimeType: 'image/png',
        caption: null,
        position: 'topleft',
        screenName: 'MoiGoroda',
    }).addTo(map);
}

export function addExternalBorderControl(map, countryCode) {
    const external_border = new L.Control({
        position: 'topright',
    });
    const container = L.DomUtil.create('div', 'custom-control-for-map');
    container.innerHTML = '<i class="fa-regular fa-square"></i>';

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
        container.title = 'Отобразить внешние границы России';

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
    container.innerHTML = '<i class="fa-regular fa-square-plus"></i>';

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
        container.title = 'Отобразить границы регионов России';

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
        this._div.innerHTML = '<div class="d-flex align-items-center justify-content-center gap-2">'
            + '<div class="spinner-border spinner-border-sm" role="status">'
            + `<span class="visually-hidden">Загрузка...</span></div><div>${label}</div></div>`;
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