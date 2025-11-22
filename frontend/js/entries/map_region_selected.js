/**
 * Реализует отображение карты региона с метками городов и границами региона.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import L from 'leaflet';
import {create_map} from '../components/map.js';
import {icon_visited_pin, icon_not_visited_pin} from '../components/icons.js';

// Стили для полигона региона
const fillOpacity = 0.1;
const fillColor = '#6382ff';
const strokeColor = '#0033ff';
const strokeOpacity = 0.3;
const strokeWidth = 2;

// Получаем код региона из DOM
const iso3166_code = document.getElementById('iso3166_code').dataset.iso3166_code;
const region_code = iso3166_code.split('-')[1];
const country_code = iso3166_code.split('-')[0];

// Массив с городами региона
// ['latitude', 'longitude', 'city name', 'is_visited']
const all_cities = window.ALL_CITIES || [];

// Массив, хранящий в себе все созданные маркеры.
// Нужен для того, чтобы отцентрировать и отмасштабировать карту.
const allMarkers = [];

// Создаём карту используя общий компонент
const map = create_map();

// Отображаем на карте все города, меняя тип иконки в зависимости от того, посещён город или нет
for (let i = 0; i < all_cities.length; i++) {
    const coordinateWidth = all_cities[i][0];
    const coordinateLongitude = all_cities[i][1];
    const city = all_cities[i][2];
    const is_visited = all_cities[i][3] === true;

    const icon = is_visited ? icon_visited_pin : icon_not_visited_pin;
    const marker = L.marker([coordinateWidth, coordinateLongitude], {icon: icon}).addTo(map);
    marker.bindTooltip(city, {direction: 'top'});

    allMarkers.push(marker);
}

// Загружаем полигон региона
const url = `${window.URL_GEO_POLYGONS}/region/hq/${country_code}/${region_code}`;
fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error(response.statusText);
        }
        return response.json();
    })
    .then(geoJson => {
        const myStyle = {
            fillOpacity: fillOpacity,
            fillColor: fillColor,
            weight: strokeWidth,
            color: strokeColor,
            opacity: strokeOpacity
        };
        const geojson = L.geoJSON(geoJson, {
            style: myStyle,
        }).addTo(map);
        
        // Если нет маркеров, центрируем карту по границам региона
        if (allMarkers.length === 0) {
            map.fitBounds(geojson.getBounds());
        }
    })
    .catch(error => {
        console.log('Произошла ошибка при загрузке границ региона:\n' + error);
    });

// Центрируем и масштабируем карту по маркерам городов
if (allMarkers.length > 0) {
    const group = new L.featureGroup([...allMarkers]);
    map.fitBounds(group.getBounds());
}
