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

export function addExternalBorderControl(map) {
    const external_border = new L.Control({
                position: 'topright'
            });
            external_border.onAdd = function (map) {
                let container = L.DomUtil.create('div', 'custom-control-for-map')

                container.title = 'Отобразить внешние границы России';
                container.innerHTML = '<i class="fa-regular fa-square"></i>';
                container.addEventListener('click', () => {
                    if (downloadedExternalBorder === undefined) {
                        fetch('https://geo-polygons.ru/country/hq/RU')
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Ошибка при получении полигонов страны')
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

export function addInternalBorderControl(map) {
    const external_border = new L.Control({
        position: 'topright'
    });
    external_border.onAdd = function (map) {
        let container = L.DomUtil.create('div', 'custom-control-for-map')

        container.title = 'Отобразить границы регионов России';
        container.innerHTML = '<i class="fa-regular fa-square-plus"></i>';
        container.addEventListener('click', () => {
            if (downloadedInternalBorder === undefined) {
                fetch(`${URL_GEO_POLYGONS}/region/lq/RU/all`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Ошибка при получении полигонов страны')
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